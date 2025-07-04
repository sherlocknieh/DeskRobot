import threading
import logging
import queue


from configs.config import config       # 导入配置文件
from modules.EventBus import EventBus   # 导入事件总线
logger = logging.getLogger("DeskRobot") # 日志工具


class DeskRobot:
    def __init__(self):
        self.tasklist: list[threading.Thread] = []  # 任务列表
        self.event_queue = queue.Queue()            # 事件队列
        self.event_bus = EventBus()                 # 事件总线

    def add_task(self, task: threading.Thread):     # 添加任务
        self.tasklist.append(task)

    def run(self):
        logger.info("DeskRobot 已启动")
        for task in self.tasklist:                  # 启动所有子任务
            task.start()
        try:        
            self.io_loop()                          # 进入终端调试循环
        except KeyboardInterrupt:
            self.stop()                             # 停止所有子任务
        logger.info("DeskRobot 已终止")

    def io_loop(self):
        while True:
            print("调试终端已启用, 输入指令以发布事件")
            print("格式: 事件类型 [参数=值] [参数:值]")
            print("例如: led_on r=0 g=1 b=0.5")
            print("例如: led_off")
            print("例如: exit")
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

    logger.info("加载 RGB 灯模块")
    from modules.mod_led_control import LEDControl
    robot.add_task(LEDControl())

    logger.info("加载温湿度模块")
    from modules.mod_temperature import Temperature
    robot.add_task(Temperature())

    logger.info("加载小车控制模块")
    from modules.mod_car_control import CarControl
    robot.add_task(CarControl())

    logger.info("加载手柄模块")
    from modules.mod_game_pad import GamePad
    robot.add_task(GamePad())

    logger.info("加载音乐播放器模块")
    logger.info("依赖的库: pip install pygame")
    from modules.mod_music_player import MusicPlayerThread
    robot.add_task(MusicPlayerThread())

    logger.info("加载语音唤醒模块")
    from modules.mod_voice_awake import AwakeThread
    robot.add_task(AwakeThread())

    logger.info("加载语音IO模块")
    from modules.mod_voice_detect import VoiceThread
    robot.add_task(VoiceThread())

    logger.info("加载 STT 模块")
    from modules.mod_voice_stt import STTThread
    robot.add_task(STTThread(config=config))

    logger.info("加载 TTS 模块")
    from modules.mod_voice_tts import TTSThread
    robot.add_task(TTSThread())

    logger.info("加载 OLED 模块")
    logger.info("依赖: pip install luma.core luma.oled pillow")
    from modules.mod_oled_image import OLEDThread
    robot.add_task(OLEDThread())

    logger.info("加载 OLED 表情模块")
    logger.info("依赖: pip install pillow")
    from modules.mod_oled_roboeyes import RoboeyesThread
    robot.add_task(RoboeyesThread())

    logger.info("加载 OLED 文本模块")
    logger.info("需安装中文字体: sudo apt install fonts-wqy-microhei")
    from modules.mod_oled_text import TextDisplayThread
    robot.add_task(TextDisplayThread())

    logger.info("加载 OLED 思考动画模块")
    from modules.mod_oled_animation import ThinkingAnimationThread
    robot.add_task(ThinkingAnimationThread())

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

    # logger.info("加载网页模块")
    # from modules.mod_web_camera import WEBCamera
    # robot.add_task(WEBCamera())

    # logger.info("加载人脸追踪模块")
    # from modules.mod_face_track import FaceTrack
    # robot.add_task(FaceTrack())


    robot.run()