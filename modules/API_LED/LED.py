"""
LED控制API

依赖的库: 
    gpiozero
    pigpio
    lgpio

可用接口:
    rgb = RGB(r_pin=10, g_pin=9, b_pin=11)  # 创建RGB对象, 并指定GPIO引脚
    rgb.off()                               # 关闭所有LED
    rgb.on(r=1, g=0, b=0)                   # 开启LED, 并设置各灯的亮度
    rgb.flash(speed=1)                      # 启动交替闪烁效果
    rgb.breeze(speed=1)                     # 启动交替呼吸效果
"""


from gpiozero import PWMLED
from threading import Thread
from time import sleep


class RGB:
    def __init__(self, r_pin=10, g_pin=9, b_pin=11): # 默认连接GPIO10, GPIO9, GPIO11
        """初始化RGB对象"""
        self._red   = PWMLED(r_pin)
        self._green = PWMLED(g_pin)
        self._blue  = PWMLED(b_pin)
        self._running = False
        self._thread = None
        self.off()

    def off(self):
        if self._thread:
            """结束正在运行的线程"""
            self._running = False
            self._thread.join()
        """关闭所有LED"""
        self._red.off()
        self._green.off()
        self._blue.off()

    def on(self, r=1.0, g=1.0, b=1.0):
        self.off()
        self._red.value = r
        self._green.value = g
        self._blue.value = b

    def flash(self, speed=1):
        """启动交替闪烁线程"""
        self.off()
        self._running = True
        self._thread = Thread(target=self._flash_loop, args=([speed]))
        self._thread.start()
    
    def breeze(self, speed=1):
        """启动交替呼吸线程"""
        self.off()
        self._running = True
        self._thread = Thread(target=self._breeze_loop, args=([speed]))
        self._thread.start()
    
    def _flash_loop(self, speed=1):
        """交替闪烁循环"""
        lights = [self._red, self._green, self._blue]
        current_color = 0
        while self._running:
            lights[current_color].on()
            if not self._running:
                break
            sleep(1/speed)
            lights[current_color].off()
            current_color = (current_color + 1) % 3

    def _breeze_loop(self, speed=1):
        """交替呼吸循环"""
        lights = [self._red, self._green, self._blue]
        current_color = 0
        brightness = 0
        direction = 1
        while self._running:
            brightness += 0.01 * direction
            if brightness >= 1.0:    # 亮度增加到1,开始减少亮度
                direction = -1
                brightness = 1.0
            elif brightness <= 0.0:  # 亮度减少到0,切换颜色,开始增加亮度
                direction = 1
                brightness = 0.0
                current_color = (current_color + 1) % 3
            lights[current_color].value = brightness # 设置当前颜色的亮度
            sleep(0.01/speed)  # 根据速度调整延时


if __name__ == '__main__':
    """
    测试代码

    将三色LED灯接到树莓派
        红: GPIO 10
        绿: GPIO 9
        蓝: GPIO 11
    """
    rgb = RGB(10, 9, 11)       # 创建RGB对象

    rgb.on(1, 1, 1)            # 开启LED, 全亮
    sleep(2)                   # 持续2秒

    rgb.flash(speed=2)         # 交替闪烁效果
    sleep(4)                   # 持续4秒
    
    rgb.breeze(speed=2)        # 交替呼吸效果
    sleep(4)                   # 持续4秒

    rgb.off()                  # 关闭所有LED
