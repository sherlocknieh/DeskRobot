"""
RoboEyes 表情生成API
这是一个包装器(Wrapper)，用于控制底层的 roboeyes.py 库。
"""

import logging
import time

from utils.config import config

from .roboeyes import ANGRY, DEFAULT, HAPPY, TIRED, RoboEyes

logger = logging.getLogger(__name__)


class RoboeyesAPI:
    """
    RoboeyesAPI 控制类
    负责初始化和控制RoboEyes动画
    """

    def __init__(self, frame_rate=50):
        """初始化RoboEyes控制器"""
        width = config.get("screen_width", 128)
        height = config.get("screen_height", 64)
        self.rbe = RoboEyes(width, height, frame_rate)
        self.expression_map = {
            "happy": HAPPY,
            "angry": ANGRY,
            "tired": TIRED,
            "default": DEFAULT,
        }
        logger.info(f"RoboeyesAPI 初始化，帧率={frame_rate}")

    def update(self):
        """
        更新一帧动画并返回图像。
        这是动画循环的核心。
        """
        return self.rbe.update()

    def set_expression(self, expression: str):
        """
        设置机器人表情

        Args:
            expression (str): 'happy', 'angry', 'tired', 'default'
        """
        mood = self.expression_map.get(expression.lower(), DEFAULT)
        self.rbe.set_mood(mood)
        return f"机器人表情设置为: {expression}"

    def trigger_quick_expression(self, expression: str):
        """
        触发一个快速、一次性的表情动画。

        Args:
            expression (str): 'laugh', 'confused'
        """
        if expression == "laugh":
            self.rbe.anim_laugh()
        elif expression == "confused":
            self.rbe.anim_confused()
        return f"机器人触发了快速表情: {expression}"

    def set_look_direction(self, direction):
        """
        设置眼睛看的方向

        Args:
            direction: N, NE, E, SE, S, SW, W, NW
        """
        # Note: Need to import directions from .roboeyes if they are defined there
        # For now, assuming they are passed in correctly.
        self.rbe.set_position(direction)

    def set_idle_mode(self, active: bool, interval=1, variation=3):
        """开启或关闭闲置模式（眼睛随机看）"""
        self.rbe.set_idle_mode(active, interval, variation)
        logger.info(f"机器人闲置模式设置为: {active}")

    def set_autoblinker(self, active: bool, interval=1, variation=4):
        """开启或关闭自动眨眼"""
        self.rbe.set_autoblinker(active, interval, variation)
        logger.info(f"机器人自动眨眼模式设置为: {active}")


if __name__ == "__main__":
    import sys
    from os import path

    # 为了能导入项目根目录下的模块 (utils, modules)
    project_root = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(project_root)

    from modules.OLED.oled_api import OLED

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("--- RoboEyes API 测试 (与 OLED API 集成) ---")

    try:
        # 1. 初始化API
        robo_api = RoboeyesAPI(frame_rate=30)
        oled_api = OLED.get_instance()
        logging.info("RoboEyes 和 OLED API 初始化成功。")

        # 2. 默认开启自动模式
        robo_api.set_autoblinker(True, interval=2, variation=3)
        robo_api.set_idle_mode(True, interval=2, variation=2)

        # 3. 启动交互式测试循环
        print("\n交互式测试已启动。")
        print("输入 'happy', 'angry', 'tired', 'default' 来改变表情。")
        print("输入 'laugh' 或 'confused' 来触发快速表情。")
        print("输入 'q' 或按 Ctrl+C 退出。")

        # 在新线程中运行输入处理，避免阻塞动画循环
        import threading

        user_input = ["default"]

        def get_input():
            while True:
                try:
                    cmd = input("> ")
                    if cmd:
                        user_input[0] = cmd.lower()
                    if user_input[0] == "q":
                        break
                except EOFError:  # 在某些IDE中，Ctrl+D会触发EOFError
                    user_input[0] = "q"
                    break

        input_thread = threading.Thread(target=get_input, daemon=True)
        input_thread.start()

        last_expression = "default"
        while user_input[0] != "q":
            start_time = time.monotonic()

            # 处理用户输入
            current_input = user_input[0]
            if current_input != last_expression:
                if current_input in robo_api.expression_map:
                    robo_api.set_expression(current_input)
                    logging.info(f"表情已设置为: {current_input}")
                elif current_input in ["laugh", "confused"]:
                    robo_api.trigger_quick_expression(current_input)
                    logging.info(f"触发快速表情: {current_input}")
                    user_input[0] = last_expression  # 快速表情是一次性的，恢复之前状态
                last_expression = current_input

            # 更新并显示图像
            image = robo_api.update()
            if image:
                oled_api.display_image(image)

            # 控制帧率
            elapsed = time.monotonic() - start_time
            sleep_time = (1.0 / 30) - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n用户中断测试。")
    except Exception as e:
        logging.error(f"RoboEyes API 测试失败: {e}", exc_info=True)
    finally:
        logging.info("--- RoboEyes API 测试结束 ---")
        if oled_api and config.get("screen_cv_simulation"):
            import cv2

            cv2.destroyAllWindows()
