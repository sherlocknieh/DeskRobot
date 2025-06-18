import logging
import threading
import time

from modules.API_EventBus import event_bus
from modules.API_EventBus.event_bus import EventBus
from configs.logging_config import setup_logging


logger = logging.getLogger(__name__)
setup_logging()

class DeskRobot:
    def __init__(self, event_bus: EventBus):
        self.name = "DeskRobot"
        self.status = "idle"
        self.threads = []
        self.event_bus = event_bus
        self.stop_event = threading.Event()

    def add_thread(self, thread: threading.Thread):
        """添加一个要管理的线程"""
        self.threads.append(thread)

    def run(self):
        """启动所有已添加的线程"""
        logger.info("DeskRobot 启动，开始启动所有线程...")
        for thread in self.threads:
            thread.start()
        logger.info("所有线程已启动。")
        logger.info("DeskRobot 正在运行。使用命令 exit 退出。")
        try:
            while True:
                # 监听 "EXIT" 事件，退出程序
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("正在退出 DeskRobot...")
            robot.stop()
            logger.info("DeskRobot 关闭完成。")

    def stop(self):
        """通过发布事件来请求所有线程停止"""
        logger.info("正在通过发布STOP_THREADS事件来停止所有线程...")
        self.event_bus.publish("STOP_THREADS")

        # 等待所有线程真正结束
        for thread in self.threads:
            thread.join()
        logger.info("所有线程已停止。")



if __name__ == "__main__":

    robot = DeskRobot(event_bus)

    # 加载终端IO模块
    from modules.mod_terminal_io import IOThread
    robot.add_thread(IOThread(event_bus))

    # # 加载OLED模块
    # from modules.mod_oled import OledThread
    # robot.add_thread(OledThread(event_bus))

    # # 加载表情模块
    # from modules.mod_roboeyes import RoboeyesThread
    # robot.add_thread(RoboeyesThread(event_bus))

    # # 加载AI模块
    # from modules.mod_ai_agent import AiThread
    # robot.add_thread(AiThread(event_bus))

    # # 加载语音模块
    # from modules.voice_threads import initialize_voice_threads
    # voice_threads = initialize_voice_threads(event_bus)
    # for thread in voice_threads:
    #    robot.add_thread(thread)

    # # 加载其他模块
    # ...
 
    # 启动
    robot.run()
