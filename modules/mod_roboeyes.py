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
- OPEN_EYES: 打开眼睛
- CLOSE_EYES: 关闭眼睛
- STOP_THREADS: 停止线程
- ENABLE_AUTOBLINKER: 开启自动眨眼
- DISABLE_AUTOBLINKER: 关闭自动眨眼
- ENABLE_IDLE_MODE: 开启闲置模式
- DISABLE_IDLE_MODE: 关闭闲置模式
- CENTER_EYES: 眼睛中置

Publish:
- UPDATE_LAYER: 更新图层显示
    - 发布眼睛动画帧到显示系统

"""

import logging
import queue
import threading
import time

from modules.API_Roboeyes.roboeyes_api import RoboeyesAPI
from modules.EventBus.event_bus import EventBus

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
        self.event_bus.subscribe("SET_EXPRESSION", self.event_queue, "OLED表情模块")
        self.event_bus.subscribe(
            "TRIGGER_QUICK_EXPRESSION", self.event_queue, "OLED表情模块"
        )
        self.event_bus.subscribe("OPEN_EYES", self.event_queue, "OLED表情模块")
        self.event_bus.subscribe("CLOSE_EYES", self.event_queue, "OLED表情模块")
        self.event_bus.subscribe("ENABLE_AUTOBLINKER", self.event_queue, "OLED表情模块")
        self.event_bus.subscribe(
            "DISABLE_AUTOBLINKER", self.event_queue, "OLED表情模块"
        )
        self.event_bus.subscribe("ENABLE_IDLE_MODE", self.event_queue, "OLED表情模块")
        self.event_bus.subscribe("DISABLE_IDLE_MODE", self.event_queue, "OLED表情模块")
        self.event_bus.subscribe("CENTER_EYES", self.event_queue, "OLED表情模块")
        self.event_bus.subscribe("STOP_THREADS", self.event_queue, "OLED表情模块")

        # 默认开启闲置和眨眼
        self.api.set_autoblinker(True)
        self.api.set_idle_mode(True, 2, 4)

    def run(self):
        """线程主循环"""
        logger.info(f"{self.name} 启动")
        self.event_bus.publish("THREAD_STARTED", name="OLED表情模块")

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
                elif event_type == "OPEN_EYES":
                    logger.info("接收到 OPEN_EYES 事件")
                    self.api.open_eyes()
                elif event_type == "CLOSE_EYES":
                    logger.info("接收到 CLOSE_EYES 事件")
                    self.api.close_eyes()
                elif event_type == "ENABLE_AUTOBLINKER":
                    logger.info("接收到 ENABLE_AUTOBLINKER 事件, 开启自动眨眼")
                    self.api.set_autoblinker(True)
                elif event_type == "DISABLE_AUTOBLINKER":
                    logger.info("接收到 DISABLE_AUTOBLINKER 事件, 关闭自动眨眼")
                    self.api.set_autoblinker(False)
                elif event_type == "ENABLE_IDLE_MODE":
                    logger.info("接收到 ENABLE_IDLE_MODE 事件, 开启闲置模式")
                    self.api.set_idle_mode(True)
                elif event_type == "DISABLE_IDLE_MODE":
                    logger.info("接收到 DISABLE_IDLE_MODE 事件, 关闭闲置模式")
                    self.api.set_idle_mode(False)
                elif event_type == "CENTER_EYES":
                    logger.info("接收到 CENTER_EYES 事件, 眼睛中置")
                    self.api.center_eyes()
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
