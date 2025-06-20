import logging
import queue
import threading

from modules.EventBus import event_bus
from modules.EventBus.event_bus import EventBus


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

    print("加载主控模块")
    robot = DeskRobot(event_bus)


    print("加载配置文件")
    """安装依赖: pip install python-dotenv"""
    from configs.config import config, setup_logging
    logger = logging.getLogger(__name__)
    setup_logging()


    print("加载 OLED 模块")
    """安装依赖: pip install luma.core luma.oled pillow"""
    from modules.mod_oled import OLEDThread
    robot.add_thread(
        OLEDThread(
            event_bus,
            config.get("oled_width", 128),
            config.get("oled_height", 64),
            config.get("oled_fps", 50),
            config.get("oled_i2c_address", 0x3C),
            config.get("oled_is_simulation", False),
        )
    )


    print("加载 OLED 文本模块")
    "安装字体: sudo apt install fonts-wqy-microhei"
    from modules.mod_text_display import TextDisplayThread
    robot.add_thread(
        TextDisplayThread(
            event_bus,
            config.get("text_renderer_font_path", "arial.ttf"),
            config.get("oled_width", 128),
            config.get("oled_height", 64),
            config.get("oled_fps", 50),
        )
    )


    print("加载 OLED 表情模块")
    "安装依赖: pip install pillow"
    from modules.mod_roboeyes import RoboeyesThread
    robot.add_thread(
        RoboeyesThread(
            event_bus,
            config.get("roboeyes_frame_rate", 50),
            config.get("roboeyes_width", 128),
            config.get("roboeyes_height", 64),
        )
    )


    # print("加载 AI Agent 模块")
    # """安装依赖 : pip install langchain langchain-openai langgraph"""
    # from modules.mod_ai_agent import AiThread
    # robot.add_thread(
    #     AiThread(
    #         event_bus,
    #         llm_base_url=config.get("llm_base_url", None),
    #         llm_api_key=config.get("llm_api_key", None),
    #         llm_model_name=config.get("llm_model_name", None),
    #     )
    # )


    print("加载 LED 三色灯模块")
    """安装依赖 : pip install gpiozero rpi-gpio lgpio"""
    from modules.mod_led import LED_Control
    robot.add_thread(LED_Control(event_bus))


    print("加载小车控制模块")  
    """安装依赖 : pip install gpiozero evdev"""
    from modules.mod_car_control import CarControl
    robot.add_thread(CarControl(event_bus))


    # print("加载语音模块")  
    # """安装依赖 : faster_whisper pyaudio vosk numpy"""
    # from modules.voice_threads import initialize_voice_threads
    # voice_threads = initialize_voice_threads(event_bus)
    # for thread in voice_threads:
    #    robot.add_thread(thread)


    # print("加载摄像头模块")
    # """安装依赖 : picamera"""
    # ...


    print("加载终端IO模块")
    from modules.mod_terminal_io import IOThread
    robot.add_thread(IOThread(event_bus))

    print("启动!")
    robot.run()
