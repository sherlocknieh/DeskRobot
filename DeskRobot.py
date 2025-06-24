import threading
import logging
import queue


from configs.config import config       # 导入配置文件
from modules.EventBus import EventBus   # 导入事件总线
logger = logging.getLogger("DeskRobot")    # 加载日志模块


class DeskRobot:
    def __init__(self):
        self.tasklist: list[threading.Thread] = [] # 任务列表
        
        self.event_queue = queue.Queue()        # 创建事件队列
        self.event_bus = EventBus()             # 加载事件总线
        self.event_bus.subscribe("EXIT", self.event_queue, "DeskRobot")   # 订阅"EXIT"消息

        self.thread_flag = threading.Event()    # 用于控制自身线程的运行状态
        # 调用 is_set() 获取状态, 初始状态为 False
        # 调用 set() 设为 True
        # 调用 clear() 设为 False
        # 调用 wait() 阻塞线程, 直到被其它线程调用 set()

    def add_thread(self, task: threading.Thread): # 添加任务
        self.tasklist.append(task)

    def run(self):
        for task in self.tasklist:  # 启动所有任务
            task.start()

        self.thread_flag.set()              # 设本线程为运行状态
        while self.thread_flag.is_set():    # 循环收取事件
            event = self.event_queue.get()  # 没有事件时阻塞
            if event["type"] == "EXIT":     # 收到"EXIT"事件
                self.stop()                 # 停止所有任务
        logger.info("DeskRobot 已退出")

    def stop(self):
        self.event_bus.publish("STOP_THREADS", "DeskRobot") # 发布"STOP_THREADS"事件
        for task in self.tasklist:
            task.join()                        # 等待所有任务结束
        logger.info("所有线程已停止")
        self.thread_flag.clear()               # 设本线程为停止状态


if __name__ == "__main__":

    logger.info("加载 DeskRobot 主模块")
    robot = DeskRobot()


    logger.info("加载RGB 灯模块")
    logger.info("依赖: pip install gpiozero rpi-gpio lgpio")
    from modules.mod_led_control import LEDControl
    robot.add_thread(LEDControl())


    # logger.info("加载 OLED 模块")
    # logger.info("依赖: pip install luma.core luma.oled pillow")
    # from modules.mod_oled import OLEDThread
    # robot.add_thread(
    #     OLEDThread(
    #         width = config.get("oled_width", 128),
    #         height = config.get("oled_height", 64),
    #         fps = config.get("oled_fps", 50),
    #         i2c_address = config.get("oled_i2c_address", 0x3C),
    #         is_simulation = config.get("oled_is_simulation", False),
    #     )
    # )


    # logger.info("加载OLED 表情模块")
    # logger.info("依赖: pip install pillow")
    # from modules.mod_roboeyes import RoboeyesThread
    # robot.add_thread(
    #     RoboeyesThread(
    #         config.get("roboeyes_frame_rate", 50),
    #         config.get("roboeyes_width", 128),
    #         config.get("roboeyes_height", 64),
    #     )
    # )


    # logger.info("加载 OLED 文本模块")
    # logger.info("依赖: sudo apt install fonts-wqy-microhei")
    # from modules.mod_text_display import TextDisplayThread
    # robot.add_thread(
    #     TextDisplayThread(
    #         config.get("text_renderer_font_path", "arial.ttf"),
    #         config.get("oled_width", 128),
    #         config.get("oled_height", 64),
    #         config.get("oled_fps", 50),
    #     )
    # )


    # logger.info("加载思考中动画模块")
    # from modules.mod_thinking_animation import ThinkingAnimationThread
    # robot.add_thread(
    #     ThinkingAnimationThread(
    #         frame_rate=config.get("thinking_animation_frame_rate", 20),
    #         width=config.get("oled_width", 128),
    #         height=config.get("oled_height", 64),
    #     )
    # )


    # logger.info("加载AI Agent 模块")
    # """依赖: pip install langchain langchain-openai langgraph"""
    # from modules.mod_ai_agent import AiThread
    # robot.add_thread(
    #     AiThread(
    #         llm_base_url=config.get("llm_base_url", None),
    #         llm_api_key=config.get("llm_api_key", None),
    #         llm_model_name=config.get("llm_model_name", None),
    #     )
    # )


    # logger.info("加载 AI Agent 模块")
    # logger.info("依赖: pip install langchain langchain-openai langgraph")
    # from modules.mod_ai_agent import AiThread
    # robot.add_thread(
    #     AiThread(
    #         llm_base_url=config.get("LLM_BASE_URL"),
    #         llm_api_key=config.get("LLM_API_KEY"),
    #         llm_model_name=config.get("LLM_MODEL_NAME"),
    #     )
    # )


    # logger.info("加载 STT 模块")
    # from modules.mod_stt import STTThread
    # robot.add_thread(
    #     STTThread(
    #         event_bus=event_bus,
    #         config=config,
    #     )
    # )


    # logger.info("加载 TTS 模块")
    # from modules.mod_tts import TTSThread
    # robot.add_thread(TTSThread(event_bus=event_bus))


    # logger.info("加载语音控制模块")
    # from modules.mod_voice import VoiceThread
    # robot.add_thread(
    #     VoiceThread(
    #         sample_rate=config.get("voice_sample_rate"),
    #         channels=config.get("voice_channels"),
    #         vad_threshold=config.get("voice_vad_threshold"),
    #         frames_per_buffer=config.get("voice_frames_per_buffer"),
    #     )
    # )


    # logger.info("加载车轮控制模块")  
    # logger.info("依赖: pip install gpiozero evdev")
    # from modules.mod_car_control import CarControl
    # robot.add_thread(CarControl())


    logger.info("加载终端IO模块")
    from modules.mod_terminal_io import IOThread
    robot.add_thread(IOThread())

    logger.info("启动系统!")
    robot.run()
