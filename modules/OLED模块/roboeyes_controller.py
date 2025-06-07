"""
RoboEyes动画控制模块，实现机器人眼睛动画的控制和更新
"""
if __name__ == "__main__":
    from roboeyes import ANGRY, DEFAULT, HAPPY, TIRED, RoboEyes
    from OLED import OLEDDisplay
else:
    from .roboeyes import ANGRY, DEFAULT, HAPPY, TIRED, RoboEyes
    from .OLED import OLEDDisplay

from time import sleep

OLED_SCREEN_WIDTH = 128
OLED_SCREEN_HEIGHT = 64
OLED_FRAMERATE = 50


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
        self.expression=DEFAULT
        _instance = self

    def run(self):
        """运行RoboEyes动画循环"""
        while True:
            image = self.rbe.update()
            self.oled_display.display_image(image)

    def set_expression(self, expression):
        """
        设置机器人表情

        Args:
            expression:'happy', 'angry', 'tired', 'surprised'
        """
        expression_map = {
            "happy": HAPPY,
            "angry": ANGRY,
            "tired": TIRED,
            "default": DEFAULT,
        }
        self.rbe.set_mood(expression_map[expression])
        self.expression=expression_map[expression]
        return f"机器人现在是{expression}表情！"


    def trigger_quick_expression(self, expression):
        expression_map = {
            "laugh": self.rbe.anim_laugh,
            "confused": self.rbe.anim_confused,
        }
        expression_map[expression]()
        return f"机器人{expression}了一下！"

    def set_mode(self, mode):
        """
        设置RoboEyes模式
        Args:
            mode: 'idle'
        """
        mode_map = {
            "idle": self.rbe.set_idle_mode
        }
        mode_map[mode]()

        ## todo
        return f"机器人现在是{mode}模式！"

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
    import threading
    from time import sleep
    try:
        rbec = RoboEyesController()

        thread = threading.Thread(target=rbec.run, args=())
        thread.start()

        print("RoboEyesController已启动")

        def curious_test():
            from roboeyes import N,NE,E,SE,S,SW,W,NW
            rbec.rbe.set_curiosity(True)
            rbec.rbe.set_position(N)
            sleep(1)
            rbec.rbe.set_position(NE)
            sleep(1)
            rbec.rbe.set_position(E)
            sleep(1)
            rbec.rbe.set_position(SE)

        def init_test():
            rbec.rbe.set_autoblinker(True, 3, 2)
            rbec.rbe.set_idle_mode(True, 1, 3)

        def quick_expression_test():
            rbec.trigger_quick_expression("laugh")
            sleep(1)
            rbec.trigger_quick_expression("confused")

        def blink_test():
            sleep(1)
            rbec.rbe.set_autoblinker(True, 1,0)


        tests={
            "init":(init_test,5,True),
            "curious":(curious_test,5,True),
            "quick_expression":(quick_expression_test,5,True),
            "blink":(blink_test,5,False),
        }
        print("测试开始")
        for test in tests:
            if tests[test][2]:
                print(f"run test: {test}")
                tests[test][0]()
                sleep(tests[test][1])
            else:
                pass
        thread.join()

        input("Press Enter to exit...")

    except KeyboardInterrupt:
        print("退出中...")
