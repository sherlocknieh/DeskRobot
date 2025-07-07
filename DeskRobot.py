import threading
import queue


from modules.EventBus import EventBus       # 导入事件总线
from configs.api_config import config       # 导入配置文件
from configs.log_config import logger       # 导入日志工具


class DeskRobot:
    def __init__(self):
        self.tasklist: list[threading.Thread] = []  # 任务列表
        self.event_queue = queue.Queue()            # 事件队列
        self.event_bus = EventBus()                 # 事件总线

    def add_task(self, task: threading.Thread):     # 添加任务
        self.tasklist.append(task)

    def run(self):
        for task in self.tasklist:                  # 启动所有子任务
            task.start()
        logger.info("DeskRobot 启动完成")
        try:        
            self.io_loop()                          # 进入终端调试循环
        except KeyboardInterrupt:
            self.stop()                             # 停止所有子任务
        logger.info("DeskRobot 已终止")

    def io_loop(self):
        while True:
            print("\n调试终端已启用, 输入指令以发布消息")
            print("格式: 消息类型 [参数=值] [参数:值]")
            print("例如: led_on r=0 g=1 b=0.5")
            print("例如: led_off")
            print("例如: exit\n")
            # 接收指令
            cmd = input('> ').strip().split()
            if not cmd: continue
            # 提取类型
            event_type = cmd[0].strip('"').replace('-', '_')
            if event_type.lower() == 'exit': break
            # 提取数据
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
            # 发布事件
            self.event_bus.publish(event_type, data, "DeskRobot")
        logger.info(f"已退出调试终端")

    def stop(self):
        self.event_bus.publish("EXIT", "DeskRobot") # 发布"EXIT"事件
        for task in self.tasklist:
            task.join(timeout = 10)                 # 等待子任务结束
            if task.is_alive():
                logger.warning(f"线程 {task.name} 未正常停止")


if __name__ == "__main__":

    robot = DeskRobot()

    # 导入各模块

    """小车模块 (包括车轮, 舵机, LED灯)
       依赖: pip install gpiozero pigpio lgpio
       依赖: sudo systemctl enable --now pigpiod
    """
    from modules.mod_car_control import CarControl
    robot.add_task(CarControl())


    """手柄模块
       依赖: pip install evdev
    """
    from modules.mod_game_pad import GamePad
    robot.add_task(GamePad())


    """温湿度模块
       依赖: pip install RPi.GPIO adafruit-circuitpython-dht
    """
    from modules.mod_temperature import Temperature
    robot.add_task(Temperature())


    """音乐播放器模块
       依赖: pip install pygame
    """
    from modules.mod_music_player import MusicPlayer
    robot.add_task(MusicPlayer())


    """OLED 基础模块
       依赖: pip install pillow luma.oled
    """
    from modules.mod_oled_image import OLEDThread
    robot.add_task(OLEDThread())

    """OLED 文本模块
       安装中文字体: sudo apt install fonts-wqy-microhei
       依赖: pip install pillow
    """
    from modules.mod_oled_text import TextDisplayThread
    robot.add_task(TextDisplayThread())

    """OLED 表情模块
       依赖: pip install pillow
    """
    from modules.mod_oled_roboeyes import RoboeyesThread
    robot.add_task(RoboeyesThread())

    """OLED 动画模块
       依赖: pip install pillow
    """
    from modules.mod_oled_animation import ThinkingAnimationThread
    robot.add_task(ThinkingAnimationThread())


    """语音输入模块
       依赖: pip install pyaudio torchaudio
    """
    from modules.mod_voice_io import VoiceThread
    robot.add_task(VoiceThread())

    """语音唤醒模块
       默认唤醒词为: "hey Jarvis"
       依赖: sudo apt install libspeex-dev libspeexdsp-dev
       依赖: pip install pyaudio torchaudio openwakeword speexdsp-ns "numpy<2"
    """
    from modules.mod_voice_awake import AwakeThread
    robot.add_task(AwakeThread())

    """TTS:文字转语音模块
       依赖: sudo apt install ffmpeg
       依赖: pip install pydub edge-tts
    """
    from modules.mod_voice_tts import TTSThread
    robot.add_task(TTSThread())

    """STT:语音转文字模块
       依赖: pip install websocket-client requests
       服务依赖: siliconflow 或 iflytek
    """
    from modules.mod_voice_stt import STTThread
    robot.add_task(STTThread(config))


    """AI Agent 模块
       依赖: pip install langchain-openai langgraph
       依赖服务: siliconflow
    """
    from modules.mod_ai_agent import AiThread
    robot.add_task(AiThread(config))


    """人脸追踪模块
        依赖: pip install opencv-python mediapipe simple_pid
    """
    from modules.mod_face_track import FaceTrack
    robot.add_task(FaceTrack())


    """网络摄像头模块
       依赖: pip install flask flask_socketio picamera2 opencv-python
    """
    from modules.mod_web_camera import WEBCamera
    robot.add_task(WEBCamera())


    # 开始运行
    robot.run()