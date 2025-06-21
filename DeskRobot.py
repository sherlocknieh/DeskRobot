import threading
import logging
import queue
import json
import sys


from modules.event_bus import EventBus


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

        self.logger = logging.getLogger(__name__) # 日志记录器, 用于打印日志, 替代 print() 函数

    def add_task(self, task: threading.Thread): # 添加任务
        self.tasklist.append(task)

    def run(self):
        for task in self.tasklist:  # 启动所有任务
            task.start()

        self.thread_flag.set()              # 设本线程为运行状态
        while self.thread_flag.is_set():    # 循环收取事件
            event = self.event_queue.get()  # 没有事件时阻塞
            if event["type"] == "EXIT":     # 收到"EXIT"事件
                self.stop()                 # 停止所有任务
        self.logger.info("DeskRobot 已退出")

    def stop(self):
        self.event_bus.publish("STOP_THREADS", "DeskRobot") # 发布"STOP_THREADS"事件
        for task in self.tasklist:
            task.join()                        # 等待所有任务结束
        self.logger.info("所有线程已停止")
        self.thread_flag.clear()               # 设本线程为停止状态


def init_config(config_file):
    """设置日志格式"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    return config_data
    

if __name__ == "__main__":


    print("初始化配置")
    config = init_config('configs/config.json')

    print("加载主控模块")
    robot = DeskRobot()


    print("加载 OLED 模块")
    print("安装依赖: pip install luma.core luma.oled pillow")
    from modules.mod_oled import OLEDThread
    robot.add_task(
        OLEDThread(
            width=128,
            height=64,
            fps=50,
            i2c_address=0x3C,
            is_simulation=False,
        )
    )

    print("加载 OLED 文本模块")
    print("安装字体: sudo apt install fonts-wqy-microhei")
    from modules.mod_text_display import TextDisplayThread
    robot.add_task(
        TextDisplayThread(
            font_path = config.get("text_renderer_font_path"),
            oled_width = 128,
            oled_height = 64,
            oled_fps = 50,
        )
    )

    print("加载 OLED 表情模块")
    print("安装依赖: pip install pillow")
    from modules.mod_roboeyes import RoboeyesThread
    robot.add_task(RoboeyesThread(frame_rate=50, width=128, height=64))


    print("加载 LED 三色灯模块")
    print("安装依赖 : pip install gpiozero rpi-gpio lgpio")
    from modules.mod_led_control import LEDControl
    robot.add_task(LEDControl())


    # print("加载小车控制模块")  
    # print("安装依赖 : pip install gpiozero evdev")
    # from modules.mod_car_control import CarControl
    # robot.add_task(CarControl())


    # print("加载 AI Agent 模块")
    # print("安装依赖 : pip install langchain langchain-openai langgraph")
    # from modules.mod_ai_agent import AiThread
    # robot.add_task(
    #     AiThread(
    #         llm_base_url=config.get("LLM_BASE_URL"),
    #         llm_api_key=config.get("LLM_API_KEY"),
    #         llm_model_name=config.get("LLM_MODEL_NAME"),
    #     )
    # )


    # print("加载语音模块")  
    # print("安装依赖 : pip install faster_whisper pyaudio vosk numpy")
    # from modules.voice_threads import initialize_voice_threads
    # voice_threads = initialize_voice_threads(event_bus)
    # for thread in voice_threads:
    #    robot.add_thread(thread)


    # print("加载摄像头模块")
    # print("安装依赖 : pip install picamera2 opencv-python flask")
    # ...


    print("加载终端IO模块")
    from modules.mod_terminal_io import IOThread
    robot.add_task(IOThread())

    print("启动!")
    robot.run()
