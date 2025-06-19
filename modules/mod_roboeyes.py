"""
RoboEyes 动画线程
负责生成眼睛动画的每一帧，并监听外部事件来改变表情。

Subscribe:
- SET_EXPRESSION: 设置表情
    - payload格式:
    {
        "expression": str  # 表情名称（如："happy", "sad", "angry", "surprised"等）
    }
- TRIGGER_QUICK_EXPRESSION: 触发快速表情
    - payload格式:
    {
        "expression": str,  # 表情名称
        "duration": float  # 表情持续时间（秒）（可选）
    }
- STOP_THREADS: 停止线程

Publish:
- UPDATE_LAYER: 更新图层显示
    - 发布眼睛动画帧到显示系统

"""

import logging
import queue
import threading
import time

from modules.API_EventBus.event_bus import EventBus
from modules.API_Roboeyes.roboeyes_api import RoboeyesAPI

logger = logging.getLogger(__name__)


class RoboeyesThread(threading.Thread):
    def __init__(self, event_bus: EventBus, frame_rate=50, width=128, height=64):
        super().__init__(daemon=True, name="RoboeyesThread")
        self.event_bus = event_bus
        self.api = RoboeyesAPI(frame_rate, width, height)
        self._stop_event = threading.Event()
        self.frame_interval = 1.0 / frame_rate

        # 创建私有事件队列并订阅
        self.event_queue = queue.Queue()
        self.event_bus.subscribe("SET_EXPRESSION", self.event_queue)
        self.event_bus.subscribe("TRIGGER_QUICK_EXPRESSION", self.event_queue)
        self.event_bus.subscribe("STOP_THREADS", self.event_queue)

        # 默认开启闲置和眨眼
        self.api.set_autoblinker(True)
        self.api.set_idle_mode(True, 2, 4)

    def run(self):
        """线程主循环"""
        logger.info(f"{self.name} 启动")
        self.event_bus.publish("THREAD_STARTED", name=self.__class__.__name__)

        while not self._stop_event.is_set():
            start_time = time.monotonic()

            # 检查是否有来自事件总线的指令
            self.handle_events()

            # 如果收到停止信号，立即退出循环
            if self._stop_event.is_set():
                break

            # 生成新的一帧动画
            image = self.api.update()

            # 如果生成了有效图像，则发布到事件总线
            if image:
                self.event_bus.publish(
                    "UPDATE_LAYER",
                    source=self.__class__.__name__,
                    layer_id="roboeyes",
                    image=image,
                    z_index=0,  # 总是在底层
                    position=(0, 0),  # 图像位置，左上角
                    duration=None,  # 持续时间为 None，表示永久显示
                )
            # 控制帧率
            elapsed_time = time.monotonic() - start_time
            sleep_time = self.frame_interval - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

        logger.info(f"{self.name} 已停止。")

    def handle_events(self):
        """处理来自事件总线的事件"""
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                event_type = event.get("type")
                payload = event.get("payload", {})

                if event_type == "STOP_THREADS":
                    logger.debug(f"{self.name} 收到停止事件。")
                    self.stop()
                    break  # 退出事件处理循环

                elif event_type == "SET_EXPRESSION":
                    expression = payload.get("expression", "default")
                    logger.info(f"接收到 SET_EXPRESSION 事件, 设置为 '{expression}'")
                    result = self.api.set_expression(expression)
                    logger.debug(f"API 调用结果: {result}")
                elif event_type == "TRIGGER_QUICK_EXPRESSION":
                    expression = payload.get("expression")
                    if expression:
                        logger.info(
                            f"接收到 TRIGGER_QUICK_EXPRESSION 事件, 触发 '{expression}'"
                        )
                        result = self.api.trigger_quick_expression(expression)
                        logger.debug(f"API 调用结果: {result}")
        except queue.Empty:
            pass  # 队列为空是正常情况
        except Exception:
            logger.error(f"{self.name} 处理事件时发生错误", exc_info=True)

    def stop(self, **kwargs):
        """请求线程停止。"""
        logger.info(f"正在请求停止 {self.name}...")
        self._stop_event.set()
