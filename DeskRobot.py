import threading
import logging
import queue


from configs.config import config       # 导入配置文件
from modules.EventBus import EventBus   # 导入事件总线
logger = logging.getLogger("DeskRobot") # 日志工具


class DeskRobot:
    def __init__(self):
        self.tasklist: list[threading.Thread] = [] # 活动任务列表
        
        self.event_queue = queue.Queue()        # 事件队列
        self.event_bus = EventBus()             # 事件总线

        self.thread_flag = threading.Event()    # 线程控制标志位
        # 调用 is_set() 获取状态, 初始状态为 False
        # 调用 set() 设为 True
        # 调用 clear() 设为 False
        # 调用 wait() 阻塞线程, 直到被其它线程调用 set()

    def add_task(self, task: threading.Thread): # 添加任务
        self.tasklist.append(task)

    def run(self):
        self.thread_flag.set()  # 设为运行状态
        logger.info("DeskRobot 已启动")

        for task in self.tasklist:  # 启动所有任务
            task.start()
        
        self.io_loop()  # 开启终端调试

        logger.info("DeskRobot 已退出")

    def stop(self):
        self.event_bus.publish("EXIT", "DeskRobot") # 发布"EXIT"事件
        for task in self.tasklist:
            task.join()                        # 等待所有任务结束
        logger.info("所有子线程已停止")
        self.thread_flag.clear()               # 设本线程为停止状态

    def io_loop(self):
        logger.info("调试终端已启动, 输入指令以发布事件")
        print("格式: 事件类型 [参数=值] [参数:值] ...")
        print("例如: led_on r=0 g=1 b=0.5")
        print("例如: led_off")
        print("例如: exit")
        while self.thread_flag.is_set():
            # 接收命令
            cmd = input('> ').strip().split()
            if not cmd:
                continue
            # 解析命令
            event_type = cmd[0].replace('-', '_')
            if event_type.lower() == 'exit':
                self.event_bus.publish("exit", "DeskRobot")
                self.stop()
                break
            # 解析参数
            data = {}
            for arg in cmd[1:]:
                if '=' in arg:
                    key, value = arg.split('=')
                elif ':' in arg:
                    key, value = arg.split(':')
                try:
                    value = float(value)
                except ValueError:
                    value = str(value)
                data[key.strip()] = value
            self.event_bus.publish(event_type, data, "终端IO模块")


if __name__ == "__main__":


    robot = DeskRobot()


    logger.info("加载 RGB 灯模块")
    logger.info("依赖: pip install gpiozero rpi-gpio lgpio")
    from modules.mod_led_control import LEDControl
    robot.add_task(LEDControl())


    logger.info("加载 OLED 模块")
    logger.info("依赖: pip install luma.core luma.oled pillow")
    from modules.mod_oled import OLEDThread
    robot.add_task(
        OLEDThread(
            width = config.get("oled_width", 128),
            height = config.get("oled_height", 64),
            fps = config.get("oled_fps", 50),
            i2c_address = config.get("oled_i2c_address", 0x3C),
            is_simulation = config.get("oled_is_simulation", False),
        )
    )


    logger.info("加载OLED 表情模块")
    logger.info("依赖: pip install pillow")
    from modules.mod_roboeyes import RoboeyesThread
    robot.add_task(
        RoboeyesThread(
            config.get("roboeyes_frame_rate", 50),
            config.get("roboeyes_width", 128),
            config.get("roboeyes_height", 64),
        )
    )


    logger.info("加载 OLED 文本模块")
    logger.info("依赖: sudo apt install fonts-wqy-microhei")
    from modules.mod_text_display import TextDisplayThread
    robot.add_task(
        TextDisplayThread(
            config.get("text_renderer_font_path", "arial.ttf"),
            config.get("oled_width", 128),
            config.get("oled_height", 64),
            config.get("oled_fps", 50),
        )
    )


    logger.info("加载思考中动画模块")
    from modules.mod_thinking_animation import ThinkingAnimationThread
    robot.add_task(
        ThinkingAnimationThread(
            frame_rate = config.get("thinking_animation_frame_rate", 20),
            width = config.get("oled_width", 128),
            height = config.get("oled_height", 64),
        )
    )


    logger.info("加载 AI Agent 模块")
    logger.info("依赖: pip install langchain langchain-openai langgraph")
    from modules.mod_ai_agent import AiThread
    robot.add_task(
        AiThread(
            llm_base_url = config["llm_base_url"],
            llm_api_key = config["llm_api_key"],
            llm_model_name = config["llm_model_name"],
        )
    )


    logger.info("加载 STT 模块")
    from modules.mod_stt import STTThread
    robot.add_task(STTThread(config=config))


    logger.info("加载 TTS 模块")
    from modules.mod_tts import TTSThread
    robot.add_task(TTSThread())


    logger.info("加载语音控制模块")
    from modules.mod_voice import VoiceThread
    robot.add_task(
        VoiceThread(
            sample_rate = config["voice_sample_rate"],
            channels = config["voice_channels"],
            vad_threshold = config["voice_vad_threshold"],
            frames_per_buffer = config["voice_frames_per_buffer"],
        )
    )


    logger.info("加载车轮控制模块")  
    logger.info("依赖: pip install gpiozero evdev")
    from modules.mod_car_control import CarControl
    robot.add_task(CarControl())

    robot.run()