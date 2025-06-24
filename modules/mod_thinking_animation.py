"""
思考动画模块
负责在AI思考时，显示一个加载动画。

Subscribe:
- START_AI_THINKING: 开始显示思考动画
- STOP_AI_THINKING: 停止显示思考动画
- EXIT: 停止线程

Publish:
- UPDATE_LAYER: 更新图层显示
    - 发布思考动画帧到显示系统
"""

import logging
import queue
import threading
import time

from .API_OLED.oled_animation_api import OledAnimationAPI
from .EventBus import EventBus

logger = logging.getLogger("思考动画模块")


class ThinkingAnimationThread(threading.Thread):
    def __init__(self, frame_rate=20, width=128, height=64):
        super().__init__(daemon=True, name="思考中动画")
        self.event_bus = EventBus()
        self.api = OledAnimationAPI(width, height)
        self._stop_event = threading.Event()
        self.frame_interval = 1.0 / frame_rate

        self.is_active = False
        self.frame_index = 0

        self.event_queue = queue.Queue()
        self.event_bus.subscribe("START_AI_THINKING", self.event_queue, self.name)
        self.event_bus.subscribe("STOP_AI_THINKING", self.event_queue, self.name)
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)

    def run(self):
        logger.info(f"{self.name} 启动")
        self.event_bus.publish("THREAD_STARTED", self.name)

        while not self._stop_event.is_set():
            start_time = time.monotonic()

            self.handle_events()

            if self.is_active:
                image = self.api.get_thinking_spinner_frame(self.frame_index)
                self.event_bus.publish(
                    "UPDATE_LAYER",
                    {
                        "source": self.name,
                        "layer_id": "thinking_spinner",
                        "image": image,
                        "position": (0, -15),
                        "z_index": 10,
                        "duration": None,  # 动画由事件控制，不自动过期
                    }
                )
                self.frame_index += 1

            elapsed_time = time.monotonic() - start_time
            sleep_time = self.frame_interval - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

        logger.info(f"{self.name} 已停止。")

    def handle_events(self):
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                event_type = event.get("type")

                if event_type == "START_AI_THINKING":
                    logger.info("接收到 START_AI_THINKING，开始动画。")
                    self.is_active = True
                    self.frame_index = 0

                elif event_type == "STOP_AI_THINKING":
                    logger.info("接收到 STOP_AI_THINKING，停止动画并删除图层。")
                    self.is_active = False
                    self.event_bus.publish("DELETE_LAYER", {"layer_id":"thinking_spinner"}, source=self.name)

                elif event_type == "EXIT":
                    self.stop()

        except queue.Empty:
            pass
        except Exception:
            logger.error(f"{self.name} 处理事件时发生错误", exc_info=True)

    def stop(self, **kwargs):
        logger.info(f"正在请求停止 {self.name}...")
        self._stop_event.set()
