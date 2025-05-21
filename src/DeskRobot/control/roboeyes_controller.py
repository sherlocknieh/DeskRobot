"""
RoboEyes动画控制模块，实现机器人眼睛动画的控制和更新
"""

import asyncio

import roboeyes
from device.oled import OLEDDisplay
from util.config import (
    OLED_FRAMERATE,
    OLED_SCREEN_HEIGHT,
    OLED_SCREEN_WIDTH,
)


class RoboEyesController:
    """
    RoboEyes控制器类
    负责初始化和控制RoboEyes动画
    """

    def __init__(self):
        """初始化RoboEyes控制器"""
        self.rbe = roboeyes.RoboEyes(
            OLED_SCREEN_WIDTH, OLED_SCREEN_HEIGHT, OLED_FRAMERATE
        )
        self.oled_display = OLEDDisplay()
        self.__setup()

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


if __name__ == "__main__":
    try:
        rbe = RoboEyesController()
        asyncio.run(rbe.run())
    except KeyboardInterrupt:
        print("退出中...")
