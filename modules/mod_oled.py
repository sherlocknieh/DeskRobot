"""
OLED 显示线程
负责监听渲染事件，并将图像显示到OLED屏幕上。
"""

import logging
import queue
import threading

from modules.API_EventBus.event_bus import EventBus
from modules.API_OLED.OLED_API import OLED

logger = logging.getLogger(__name__)


class OledThread(threading.Thread):
    def __init__(self, event_bus: EventBus,width=128, height=64, i2c_address=0x3C, is_simulation=False):
        super().__init__(daemon=True, name="OledThread")
        self.event_bus = event_bus
        self.api = OLED.get_instance(
            width=width,
            height=height,
            i2c_address=i2c_address,
            is_simulation=is_simulation
        )
        self.event_queue = queue.Queue()
        event_bus.subscribe("DISPLAY_IMAGE", self.event_queue)
        event_bus.subscribe("STOP_THREADS", self.event_queue)

    def run(self):
        """线程主循环"""
        logger.info("OledThread 启动")
        #self.event_bus.publish("THREAD_STARTED", name=self.__class__.__name__)

        while True:
            try:
                event = self.event_queue.get(timeout=1)
                event_type = event.get("type")

                if event_type == "STOP_THREADS":
                    logger.info("OledThread 已停止。")
                    break
                elif event_type == "DISPLAY_IMAGE":
                    image = event.get("payload", {}).get("image")
                    if image is not None:
                        self.api.display_image(image)
                    else:
                        logger.warning("收到了DISPLAY_IMAGE事件，但缺少图像数据。")

            except queue.Empty:
                # 队列超时为空，是正常现象
                continue
            except Exception as e:
                logger.error(f"OledThread 发生错误: {e}", exc_info=True)

    def stop(self, **kwargs):
        """请求线程停止。"""
        logger.info(f"正在请求停止 {self.name}...")
        self._stop_event.set()
