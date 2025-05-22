"""
RoboEyes动画控制模块，实现机器人眼睛动画的控制和更新
"""

import asyncio

from roboeyes import ANGRY, DEFAULT, HAPPY, TIRED, RoboEyes
from util.config import (
    OLED_FRAMERATE,
    OLED_SCREEN_HEIGHT,
    OLED_SCREEN_WIDTH,
)

from ..device.oled import OLEDDisplay

# 全局单例实例
_instance = None


class RoboEyesController:
    """
    RoboEyes控制器类
    负责初始化和控制RoboEyes动画
    实现为单例模式，确保全局只有一个实例
    """

    def __init__(self):
        """初始化RoboEyes控制器"""
        global _instance
        if _instance is not None:
            raise RuntimeError(
                "尝试创建RoboEyesController的多个实例。请使用get_instance()方法获取实例。"
            )

        self.rbe = RoboEyes(OLED_SCREEN_WIDTH, OLED_SCREEN_HEIGHT, OLED_FRAMERATE)
        self.oled_display = OLEDDisplay.get_instance()
        self.__setup()
        _instance = self

    def __del__(self):
        """析构函数，在对象被销毁时调用"""
        try:
            self.oled_display.cleanup()
            print("RoboEyes资源已清理")
        except Exception as e:
            print(f"清理RoboEyes资源时出错: {e}")

    def __setup(self, auto_blink=True, idle_mode=True, blink_min=3, blink_max=2):
        """
        设置RoboEyes参数

        Args:
            auto_blink: 是否自动眨眼
            idle_mode: 是否启用闲置模式
            blink_min: 眨眼最小间隔时间(秒)
            blink_max: 眨眼最大间隔时间(秒)
        """
        if auto_blink:
            self.rbe.set_autoblinker(True, blink_min, blink_max)

        if idle_mode:
            self.rbe.set_idle_mode(True, blink_min, blink_max)

        print("RoboEyes控制器已初始化")

    async def run(self):
        """运行RoboEyes动画循环"""
        while True:
            image = self.rbe.update()
            self.oled_display.display_image(image)

    def set_expression(self, expression):
        """
        设置机器人表情

        Args:
            expression: 表情名称，如'happy', 'angry', 'tired', 'surprised'等
        """
        if expression == "happy":
            # 设置为快乐表情
            self.rbe.set_mood(HAPPY)
            return "机器人现在快乐！"
        elif expression == "angry":
            # 设置为生气表情
            self.rbe.set_mood(ANGRY)
            return "机器人现在生气！"
        elif expression == "tired":
            # 设置为疲惫表情
            self.rbe.set_mood(TIRED)
            return "机器人现在疲惫！"
        elif expression == "default":
            # 设置为默认表情
            self.rbe.set_mood(DEFAULT)
            return "机器人现在是默认表情！（无表情）"
        else:
            # 设置为默认表情
            self.rbe.set_mood(DEFAULT)
            return "机器人没有这个表情！已设置为默认表情。"

    @staticmethod
    def get_instance():
        """
        获取RoboEyesController的单例实例

        Returns:
            RoboEyesController: 单例实例
        """
        global _instance
        if _instance is None:
            _instance = RoboEyesController()
        return _instance


if __name__ == "__main__":
    try:
        rbe = RoboEyesController()
        asyncio.run(rbe.run())
    except KeyboardInterrupt:
        print("退出中...")
