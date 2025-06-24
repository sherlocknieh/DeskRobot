"""
OLED 显示线程
负责监听渲染事件，并将图像显示到OLED屏幕上。

subscribe:
- UPDATE_LAYER: 更新或创建图层
    - data格式:
  {
    "layer_id": str,  # 图层唯一标识符
    "image": PIL.Image.Image,  # 要显示的图像
    "z_index": int,  # 图层的Z轴索引
    "position": tuple,  # 图像在屏幕上的位置 (x, y)
    "duration": int  # 图像显示的持续时间（秒）
  }
- SET_LAYER_VISIBILITY: 设置图层可见性
    - data格式:
  {
    "layer_id": str,  # 图层唯一标识符
    "visible": bool  # 图层是否可见
  }
- DELETE_LAYER: 删除图层
    - data格式:
    {
    "layer_id": str  # 图层唯一标识符
    }
- EXIT: 停止线程

"""

import logging
import queue
import threading
import time

from PIL import Image, ImageDraw, ImageFont
if __name__ != "__main__":
    from .API_OLED.OLED_API import OLED
    from .EventBus import EventBus

logger = logging.getLogger("OLED模块")


class Layer:
    def __init__(self, image, z_index, position, duration=None):
        """
        图层类，用于管理显示的图像、位置和持续时间。
        param image: PIL.Image.Image - 要显示的图像。
        param z_index: int - 图层的Z轴索引，决定图像的显示顺序。
        param position: tuple - 图像在屏幕上的位置，格式为 (x, y)。
        param duration: int - 图像显示的持续时间（秒），如果为 None，则永久显示。
        例如：Layer(image, z_index=1, position=(0, 0), duration=5)
        这将创建一个图层，显示在屏幕左上角 (0, 0)，Z轴索引为1，持续时间为5秒。
        """
        self.image = image
        self.z_index = z_index
        self.position = position
        self.visible = True
        self.expiry_time = time.time() + duration if duration else None

    def update(self, image, z_index=None, position=None, duration=None):
        """
        更新图层的属性。
        param image: PIL.Image.Image - 新的图像。
        param z_index: int - 新的Z轴索引，默认为当前值。
        param position: tuple - 新的位置，格式为 (x, y)，默认为当前位置。
        param duration: int - 新的持续时间（秒），默认为当前值。
        """
        self.image = image
        if z_index is not None:
            self.z_index = z_index
        if position is not None:
            self.position = position
        if duration is not None:
            self.expiry_time = time.time() + duration


class OLEDThread(threading.Thread):
    def __init__(
        self,
        width=128,
        height=64,
        fps=50,
        i2c_address=0x3C,
        is_simulation=False,
    ):
        super().__init__(daemon=True)
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_duration = 1.0 / fps

        self.oled_device = OLED.get_instance(
            width=width,
            height=height,
            i2c_address=i2c_address,
            is_simulation=is_simulation,
        )
        self.layers = {}  # 存储所有图层，用 layer_id 作为 key
        self.event_bus = EventBus()
        self.event_queue = queue.Queue()  # 用于接收来自事件监听器的请求
        self.needs_render = threading.Event()  # 用于通知渲染线程需要重新合成
        self._stop_event = threading.Event()

        self.event_bus.subscribe("UPDATE_LAYER", self.event_queue, "OLED模块")
        self.event_bus.subscribe("SET_LAYER_VISIBILITY", self.event_queue, "OLED模块")
        self.event_bus.subscribe("DELETE_LAYER", self.event_queue, "OLED模块")
        self.event_bus.subscribe("EXIT", self.event_queue, "OLED模块")

    def run(self):
        """线程主循环"""
        last_render_time = 0
        while not self._stop_event.is_set():
            try:
                self._check_expirations()
                self._process_event_queue()

                # 如果有渲染需求且达到了帧率要求
                if self.needs_render.is_set() and (
                    time.time() - last_render_time > self.frame_duration
                ):
                    self.needs_render.clear()  # 重置事件

                    final_frame = self._composite_layers()
                    self.oled_device.display_image(final_frame)
                    last_render_time = time.time()

                # 短暂休眠，避免CPU占用过高
                time.sleep(0.01)

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"OLEDThread 发生错误: {e}", exc_info=True)

    def stop(self):
        """请求线程停止。"""
        logger.info("OLEDThread 正在停止...")
        self._stop_event.set()
        self.event_bus.publish("THREAD_STOPPED", source=self.__class__.__name__)
        logger.info("OLEDThread 已停止。")

    def _process_event_queue(self):
        # 处理队列中的所有待办事项
        while not self.event_queue.empty():
            event = self.event_queue.get()
            # event["type"] & event["data"]  # 获取事件类型和负载
            if event["type"] == "UPDATE_LAYER":
                layer_id = event["data"]["layer_id"]
                image = event["data"]["image"]
                z_index = event["data"]["z_index"]
                position = event["data"]["position"]
                duration = event["data"].get("duration")

                if layer_id in self.layers:
                    self.layers[layer_id].update(image, z_index, position, duration)
                else:
                    self.layers[layer_id] = Layer(image, z_index, position, duration)

                self.needs_render.set()
            elif event["type"] == "SET_LAYER_VISIBILITY":
                layer_id = event["data"]["layer_id"]
                visible = event["data"]["visible"]

                if layer_id in self.layers:
                    self.layers[layer_id].visible = visible
                    self.needs_render.set()
            elif event["type"] == "DELETE_LAYER":
                layer_id = event["data"]["layer_id"]
                if layer_id in self.layers:
                    del self.layers[layer_id]
                    self.needs_render.set()  # 触发重绘以确保图层消失
            elif event["type"] == "EXIT":
                self.stop()
            else:
                logger.warning(f"未知事件类型: {event['type']}")

    def _check_expirations(self):
        # 检查并移除过期的图层
        now = time.time()
        expired_layers = [
            layer_id
            for layer_id, layer in self.layers.items()
            if layer.expiry_time and now >= layer.expiry_time
        ]
        if expired_layers:
            for layer_id in expired_layers:
                del self.layers[layer_id]
            self.needs_render.set()  # 需要重新渲染

    def _composite_layers(self):
        # 核心：合成图层
        # 创建一个空白的基底图像
        final_image = Image.new("1", (self.width, self.height), 0)

        # 按 z_index 排序图层
        sorted_layers = sorted(self.layers.values(), key=lambda layer: layer.z_index)

        for layer in sorted_layers:
            if layer.visible and layer.image:
                # For monochrome displays, convert image if necessary
                if layer.image.mode != "1":
                    layer_image = layer.image.convert("1")
                else:
                    layer_image = layer.image

                # Use PIL's logical operations for proper blending
                # Create a temporary image to hold the layer at the correct position
                temp_image = Image.new("1", (self.width, self.height), 0)

                # Paste the layer image onto the temporary image
                x, y = layer.position
                layer_width, layer_height = layer_image.size

                # Ensure the layer fits within bounds
                if (
                    x < self.width
                    and y < self.height
                    and x + layer_width > 0
                    and y + layer_height > 0
                ):
                    # Crop the layer if it extends beyond bounds
                    crop_x = max(0, -x)
                    crop_y = max(0, -y)
                    paste_x = max(0, x)
                    paste_y = max(0, y)

                    end_x = min(x + layer_width, self.width)
                    end_y = min(y + layer_height, self.height)

                    if crop_x < layer_width and crop_y < layer_height:
                        cropped_layer = layer_image.crop(
                            (
                                crop_x,
                                crop_y,
                                crop_x + (end_x - paste_x),
                                crop_y + (end_y - paste_y),
                            )
                        )
                        temp_image.paste(cropped_layer, (paste_x, paste_y))

                # Use logical OR to combine with final image
                from PIL import ImageChops

                final_image = ImageChops.logical_or(final_image, temp_image)

        return final_image


if __name__ == "__main__":
    
    from PIL import Image, ImageDraw, ImageFont
    from EventBus import EventBus
    from API_OLED.OLED_API import OLED

    # ==================================================================
    # 测试 OLEDThread 的功能
    # ==================================================================
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
    )


    # 创建并启动OLED管理线程，并将事件总线实例传入
    oled_thread = OLEDThread(width=128, height=64, fps=15)
    oled_thread.start()

    # !!! 关键：等待 OLED 线程准备就绪后再发布事件，避免竞态条件 !!!
    logger.info("主线程: OLEDThread 已就绪。开始发布测试事件。")

    try:
        # --- 测试用例 1: 显示一个基础图层 (模拟机器人的眼睛) ---
        logger.info("主线程: 【测试1】发布基础图层 'eyes'...")
        base_image = Image.new("1", (128, 64), 0)
        draw = ImageDraw.Draw(base_image)
        draw.rectangle((28, 20, 58, 44), outline=1, fill=0)  # 左眼
        draw.rectangle((70, 20, 100, 44), outline=1, fill=0)  # 右眼
        oled_thread.event_bus.publish(
            "UPDATE_LAYER",
            {
                "layer_id": "eyes",
                "image": base_image,
                "z_index": 0,
                "position": (0, 0),
            },
        )
        time.sleep(3)

        # --- 测试用例 2: 在上层显示一个带时效的文本信息 ---
        logger.info("主线程: 【测试2】发布临时文本图层 'info_text' (5秒后消失)...")
        text_image = Image.new("1", (100, 16), 0)  # 创建一个背景透明的图层
        draw = ImageDraw.Draw(text_image)
        # 使用更清晰的默认字体
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font = ImageFont.load_default()
        draw.text((0, 0), "Hello, Layers!", font=font, fill=1)
        oled_thread.event_bus.publish(
            "UPDATE_LAYER",
            {
                "layer_id": "info_text",
                "image": text_image,
                "z_index": 5,
                "position": (14, 24),
                "duration": 5,  # 5秒后自动消失
            },
        )
        logger.info("主线程: 等待文本图层自动消失...")

        # 让主线程在这里持续运行，以便接收 Ctrl+C
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("主线程: 检测到 Ctrl+C，正在干净地关闭程序...")
    finally:
        logger.info("主线程: 程序结束。守护线程将自动退出。")
        # 因为线程是守护线程(daemon), 主线程结束时它会自动退出。
        # 在一个完整的应用中，你可能需要一个更优雅的停止机制，比如发送STOP事件。
        pass
