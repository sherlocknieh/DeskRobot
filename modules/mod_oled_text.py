"""
文本显示线程
负责处理文本显示请求，支持滚动文本和静态文本显示。
需安装中文字体: sudo apt install fonts-wqy-microhei

Subscribe:
- SUB_TEXT_DISPLAY_REQUEST: 滚动文本显示请求
    - data格式:
    {
        "text_id": str,  # 滚动文本唯一标识符（可选）
        "text": str,  # 要显示的文本内容
        "font_size": int,  # 字体大小（默认16）
        "scroll_direction": str,  # 滚动方向："horizontal"或"vertical"
        "scroll_speed": int,  # 滚动速度（默认1）
        "loop": bool,  # 是否循环滚动（默认True）
        "layer_id": str,  # 图层ID
        "z_index": int,  # 图层深度（默认0）
        "position": tuple,  # 显示位置 (x, y)（默认(0, 0)）
        "duration": float  # 显示持续时间（秒）（可选）
    }
- SUB_TEXT_DISPLAY_CANCEL: 取消滚动文本显示
    - data格式:
    {
        "text_id": str  # 要取消的滚动文本标识符
    }
- SUB_TEXT_STATIC_DISPLAY: 静态文本显示请求
    - data格式:
    {
        "text": str,  # 要显示的文本内容
        "font_size": int,  # 字体大小（默认16）
        "layer_id": str,  # 图层ID（可选，自动生成）
        "z_index": int,  # 图层深度（默认10）
        "position": tuple,  # 显示位置 (x, y)（默认(0, 0)）
        "align": str,  # 水平对齐："left", "center", "right"（默认"center"）
        "valign": str,  # 垂直对齐："top", "center", "bottom"（默认"center"）
        "wrap": bool,  # 是否自动换行（默认True）
        "image_width": int,  # 图像宽度（默认OLED宽度）
        "image_height": int,  # 图像高度（默认OLED高度）
        "duration": float,  # 显示持续时间（秒）（None表示永久显示）
        "text_color": int,  # 文本颜色（单色）（默认1白色）
        "bg_color": int  # 背景颜色（单色）（默认0黑色）
    }
- EXIT: 停止线程

Publish:
- UPDATE_LAYER: 更新图层显示
- DELETE_LAYER: 删除图层

"""

import logging
import threading
import time
import uuid
from queue import Empty, Queue

from .EventBus import EventBus
from .API_OLED.text_renderer import TextRenderer
from .API_OLED.text_scroller import TextScroller

logger = logging.getLogger("OLED文本")


class TextDisplayThread(threading.Thread):
    def __init__(
        self,
        font_path = "wqy-microhei",
        oled_width: int = 128,
        oled_height: int = 64,
        oled_fps: int = 50,
    ):
        super().__init__(daemon=True)
        self.name = "OLED文本"
        self.event_bus = EventBus()
        self._stop_event = threading.Event()
        self.active_scrolls = {}

        # Store config values
        self.oled_width = oled_width
        self.oled_height = oled_height
        self.oled_fps = oled_fps

        # Initialize renderer with font path
        self.renderer = TextRenderer(
            font_path
        )  # Create private queue and subscribe to events
        self.event_queue = Queue()
        self.event_bus.subscribe("SUB_TEXT_DISPLAY_REQUEST", self.event_queue, self.name)
        self.event_bus.subscribe("SUB_TEXT_DISPLAY_CANCEL", self.event_queue, self.name)
        self.event_bus.subscribe("SUB_TEXT_STATIC_DISPLAY", self.event_queue, self.name)  # 新增：静态文本显示
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)

    def run(self):
        logger.info(f"{self.name} started.")
        while not self._stop_event.is_set():
            try:
                # Process events from the queue
                event = self.event_queue.get(timeout=1)
                event_type = event.get("type")
                data = event.get("data", {})

                if event_type == "SUB_TEXT_DISPLAY_REQUEST":
                    self._handle_display_request(data)
                elif event_type == "SUB_TEXT_DISPLAY_CANCEL":
                    self._handle_cancel_request(data)
                elif event_type == "SUB_TEXT_STATIC_DISPLAY":
                    self._handle_static_display_request(data)
                elif event_type == "EXIT":
                    self.stop()
                    break
            except Empty:
                # This is normal, just means no events for a second
                continue
            except Exception as e:
                logger.error(f"{self.name} caught an exception: {e}", exc_info=True)
        logger.info(f"{self.name} has stopped.")

    def stop(self):
        logger.info(f"Stopping {self.name}...")
        self._stop_event.set()
        # Stop all active scrolling child threads
        for text_id, scroll_info in list(self.active_scrolls.items()):
            scroll_info["stop_event"].set()

    def _handle_display_request(self, data):
        text_id = data.get("text_id", f"text-scroll-{uuid.uuid4()}")

        # If a scroll with the same ID is active, cancel it first
        if text_id in self.active_scrolls:
            self._cancel_scroll(text_id)

        scroll_thread = threading.Thread(
            target=self._scroll_task, args=(text_id, data), daemon=True
        )

        stop_event = threading.Event()
        self.active_scrolls[text_id] = {
            "thread": scroll_thread,
            "stop_event": stop_event,
            "layer_id": data.get("layer_id"),
        }
        scroll_thread.start()
        logger.info(f"Started text scroll task: {text_id}")

    def _handle_cancel_request(self, data):
        text_id = data.get("text_id")
        if text_id in self.active_scrolls:
            self._cancel_scroll(text_id)
            logger.info(f"Cancelled text scroll task via event: {text_id}")

    def _cancel_scroll(self, text_id):
        if text_id in self.active_scrolls:
            scroll_info = self.active_scrolls[text_id]
            scroll_info["stop_event"].set()  # Signal the thread to stop
            # The thread will clean itself up

    def _scroll_task(self, text_id, data):
        scroller = TextScroller(
            renderer=self.renderer,
            text=data.get("text", ""),
            font_size=data.get("font_size", 16),
            viewport_width=self.oled_width,
            viewport_height=self.oled_height,
            scroll_direction=data.get("scroll_direction", "horizontal"),
            scroll_speed=data.get("scroll_speed", 1),
            loop=data.get("loop", True),
        )

        layer_id = data.get("layer_id")
        z_index = data.get("z_index", 0)
        position = data.get("position", (0, 0))
        duration = data.get("duration")

        # Ensure text_id exists before trying to access it
        if text_id not in self.active_scrolls:
            logger.warning(
                f"Scroll task {text_id} started but was cancelled before it could run."
            )
            return
        stop_event = self.active_scrolls[text_id]["stop_event"]

        start_time = time.time()
        frame_interval = 1 / self.oled_fps

        while not stop_event.is_set():
            # Check for duration timeout
            if duration and (time.time() - start_time) > duration:
                break

            frame = scroller.next_frame()

            if frame is None:  # Animation finished naturally (non-looping)
                break

            self.event_bus.publish(
                "UPDATE_LAYER",
                {
                    "layer_id": layer_id,
                    "image": frame,
                    "z_index": z_index,
                    "position": position,
                }
            )

            time.sleep(frame_interval)

        # --- Cleanup ---
        logger.info(f"Text scroll task finished or cancelled: {text_id}")
        self.event_bus.publish("DELETE_LAYER", layer_id=layer_id)
        if text_id in self.active_scrolls:
            del self.active_scrolls[text_id]

    def _handle_static_display_request(self, data):
        """
        处理静态文本显示请求

        data参数：
        - text: 要显示的文本内容
        - font_size: 字体大小，默认16
        - layer_id: 图层ID，用于标识此文本层
        - z_index: 图层深度，默认10
        - position: 显示位置 (x, y)，默认(0, 0)
        - align: 文本对齐方式，默认"center"
        - valign: 垂直对齐方式，默认"center"
        - wrap: 是否自动换行，默认True
        - image_width: 图像宽度，默认为OLED宽度
        - image_height: 图像高度，默认为OLED高度
        - duration: 显示持续时间（秒），None表示永久显示
        - text_color: 文本颜色（单色），默认1（白色）
        - bg_color: 背景颜色（单色），默认0（黑色）
        """
        try:
            # 从data中提取参数，设置默认值
            text = data.get("text", "")
            font_size = data.get("font_size", 16)
            layer_id = data.get("layer_id", f"static-text-{uuid.uuid4()}")
            z_index = data.get("z_index", 10)
            position = data.get("position", (0, 0))
            align = data.get("align", "center")
            valign = data.get("valign", "center")
            wrap = data.get("wrap", True)
            image_width = data.get("image_width", self.oled_width)
            image_height = data.get("image_height", self.oled_height)
            duration = data.get("duration")  # None means display permanently
            text_color = data.get("text_color", 1)  # White text
            bg_color = data.get("bg_color", 0)  # Black background

            if not text:
                logger.warning("Static text display request with empty text, ignoring.")
                return

            # 使用TextRenderer渲染文本
            static_image = self.renderer.render_text(
                text=text,
                font_size=font_size,
                image_width=image_width,
                image_height=image_height,
                text_color=text_color,
                bg_color=bg_color,
                align=align,
                valign=valign,
                wrap=wrap,
            )

            # 发布图层更新事件，显示静态文本
            self.event_bus.publish(
                "UPDATE_LAYER",
            {
                "layer_id": layer_id,
                "image": static_image,
                "z_index": z_index,
                "position": position,
                "duration": duration,  # 如果指定了持续时间，图层会自动过期
            }
            )

            logger.info(
                f"Displayed static text on layer '{layer_id}': '{text[:50]}{'...' if len(text) > 50 else ''}'"
            )

            # 如果没有指定持续时间，记录这个静态文本以便后续管理
            if duration is None:
                logger.debug(
                    f"Static text '{layer_id}' will display permanently until manually removed"
                )

        except Exception as e:
            logger.error(
                f"Error handling static text display request: {e}", exc_info=True
            )
