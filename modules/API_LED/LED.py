from gpiozero import PWMLED
from threading import Thread
from time import sleep


"""LED控制API

依赖的库: gpiozero

可用接口:

rgb = RGB(r_pin=10, g_pin=9, b_pin=11)  # 创建RGB对象
rgb.on(r=1, g=0, b=0)                   # 开启LED, 并控制各灯的亮度
rgb.off()                               # 关闭所有LED
rgb.flash(speed=1)                      # 交替闪烁效果
rgb.breeze(speed=1)                     # 交替呼吸效果

"""

class RGB:
    def __init__(self, r_pin=10, g_pin=9, b_pin=11):

        self._red   = PWMLED(r_pin)
        self._green = PWMLED(g_pin)
        self._blue  = PWMLED(b_pin)
        self._thread = None
        self._running = False
        self.off()

    def off(self):
        """结束正在运行的线程"""
        if self._thread:
            self._running = False
            self._thread.join()
        """关闭所有LED"""
        self._red.off()
        self._green.off()
        self._blue.off()

    def on(self, r=1.0, g=1.0, b=1.0):
        self.off()
        print('LED On, RGB:', r, g, b)
        self._red.value = r
        self._green.value = g
        self._blue.value = b

    def flash(self, speed=1):
        """交替闪烁效果"""
        self.off()
        self._running = True
        self._thread = Thread(target=self._flash_loop, args=([speed]))
        self._thread.start()
    
    def breeze(self, speed=1):
        """交替呼吸效果"""
        self.off()
        self._running = True
        self._thread = Thread(target=self._breeze_loop, args=([speed]))
        self._thread.start()
    
    def _flash_loop(self, speed=1):
        print('Flash On, Speed:', speed)
        lights = [self._red, self._green, self._blue]
        current_color = 0
        while self._running:
            lights[current_color].on()
            if not self._running:
                break
            sleep(1/speed)
            lights[current_color].off()
            current_color = (current_color + 1) % 3
        print('Flash Off')

    def _breeze_loop(self, speed=1):
        print('Breeze On, Speed:', speed)
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
        print('Breeze Off')



if __name__ == '__main__':

    """测试代码"""

    rgb = RGB(10, 9, 11)       # 创建RGB对象

    rgb.on(1, 1, 1)            # 开启LED, 全亮
    sleep(2)

    rgb.flash(speed=2)         # 交替闪烁效果
    sleep(4)
    
    rgb.breeze(speed=2)        # 交替呼吸效果
    sleep(4)

    rgb.off()                  # 关闭所有LED
