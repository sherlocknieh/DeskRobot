"""
RoboEyes 表情生成API
这是一个包装器(Wrapper)，用于控制底层的 roboeyes.py 库。
"""

import logging

from .roboeyes import ANGRY, DEFAULT, HAPPY, TIRED, RoboEyes

logger = logging.getLogger("Roboeyes")


class RoboeyesAPI:
    """
    RoboeyesAPI 控制类
    负责初始化和控制RoboEyes动画
    """

    def __init__(self, frame_rate, width, height):
        """初始化RoboEyes控制器"""
        self.rbe = RoboEyes(width, height, frame_rate)
        self.expression_map = {
            "happy": HAPPY,
            "angry": ANGRY,
            "tired": TIRED,
            "default": DEFAULT,
        }
        logger.info(f"Roboeyes 初始化，帧率={frame_rate}")

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

    def open_eyes(self):
        """打开眼睛"""
        self.rbe.open_eyes()

    def close_eyes(self):
        """关闭眼睛"""
        self.rbe.close_eyes()

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

    def center_eyes(self):
        """将眼睛位置设置为中置"""
        self.rbe.set_position(DEFAULT)

    def set_idle_mode(self, active: bool, interval=1, variation=3):
        """开启或关闭闲置模式（眼睛随机看）"""
        self.rbe.set_idle_mode(active, interval, variation)
        logger.info(f"机器人闲置模式设置为: {active}")

    def set_autoblinker(self, active: bool, interval=1, variation=4):
        """开启或关闭自动眨眼"""
        self.rbe.set_autoblinker(active, interval, variation)
        logger.info(f"机器人自动眨眼模式设置为: {active}")


if __name__ == "__main__":
    pass
