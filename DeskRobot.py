import logging
import queue
import threading

#from configs.config import config
from configs.logging_config import setup_logging
from modules.EventBus import event_bus
from modules.EventBus.event_bus import EventBus

logger = logging.getLogger(__name__)
setup_logging()


class DeskRobot:
    def __init__(self, event_bus: EventBus):
        self.threads = []
        self.event_bus = event_bus
        self.stop_event = threading.Event()
        self.event_queue = queue.Queue()
        self.event_bus.subscribe("EXIT", self.event_queue)

    def add_thread(self, thread: threading.Thread):
        """添加一个要管理的线程"""
        self.threads.append(thread)

    def run(self):
        """启动所有已添加的线程"""
        logger.info("DeskRobot 启动，开始启动所有线程...")
        for thread in self.threads:
            thread.start()

        while True:
            event = self.event_queue.get()
            if event["type"] == "EXIT":
                self.stop()
                break
        print("DeskRobot 已退出。")

    def stop(self):
        logger.info("正在通过发布STOP_THREADS事件来停止所有线程...")
        self.event_bus.publish("STOP_THREADS")
        for thread in self.threads:
            thread.join()
        logger.info("所有线程已停止")


if __name__ == "__main__":
    robot = DeskRobot(event_bus)


    # # OLED模块  # 依赖第三方库 :  rpi-gpio pillow adafruit-circuitpython-ssd1306
    # from modules.mod_oled import OLEDThread
    # robot.add_thread(
    #     OLEDThread(
    #         event_bus,
    #         config.get("oled_width", 128),
    #         config.get("oled_height", 64),
    #         config.get("oled_fps", 50),
    #         config.get("oled_i2c_address", 0x3C),
    #         config.get("oled_is_simulation", False),
    #     )
    # )

    # # 表情模块  # 依赖第三方库 : pillow
    # from modules.mod_roboeyes import RoboeyesThread
    # robot.add_thread(
    #     RoboeyesThread(
    #         event_bus,
    #         config.get("roboeyes_frame_rate", 50),
    #         config.get("roboeyes_width", 128),
    #         config.get("roboeyes_height", 64),
    #     )
    # )

    # # AI模块  # 依赖第三方库 : langchain langchain-openai langgraph
    # from modules.mod_ai_agent import AiThread

    # robot.add_thread(
    #     AiThread(
    #         event_bus,
    #         llm_base_url=config.get("llm_base_url", None),
    #         llm_api_key=config.get("llm_api_key", None),
    #         llm_model_name=config.get("llm_model_name", None),
    #     )
    # )

    # # 语音模块  # 依赖第三方库 : faster_whisper pyaudio vosk numpy
    # from modules.voice_threads import initialize_voice_threads
    # voice_threads = initialize_voice_threads(event_bus)
    # for thread in voice_threads:
    #    robot.add_thread(thread)

    # # 其他模块  # 依赖第三方库 :
    # ...

    # # 文本显示模块
    # from modules.mod_text_display import TextDisplayThread

    # robot.add_thread(
    #     TextDisplayThread(
    #         event_bus,
    #         config.get("text_renderer_font_path", "arial.ttf"),
    #         config.get("oled_width", 128),
    #         config.get("oled_height", 64),
    #         config.get("oled_fps", 50),
    #     )
    # )

    # LED模块  # 依赖第三方库 : gpiozero rpi-gpio lgpio
    # from modules.mod_led import LED_Control
    # robot.add_thread(LED_Control(event_bus))

    # 小车控制模块  # 依赖第三方库 : gpiozero evdev
    from modules.mod_car_control import CarControl
    robot.add_thread(CarControl(event_bus))

    # 终端IO模块
    from modules.mod_terminal_io import IOThread
    robot.add_thread(IOThread(event_bus))

    # 启动
    robot.run()
