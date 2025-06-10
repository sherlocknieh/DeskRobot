from gpiozero import PWMLED
from time import sleep
from threading import Thread

class RGB:
    def __init__(self, r_pin=13, g_pin=19, b_pin=26):
        # 引脚初始化
        self.red   = PWMLED(r_pin)
        self.green = PWMLED(g_pin)
        self.blue  = PWMLED(b_pin)
        # 初始状态
        self.red.off()
        self.green.off()
        self.blue.off()
        # 公共状态
        self.status = {'mode': 'off','speed': 1}
    
    def off(self):
        self.red.off()
        self.green.off()
        self.blue.off()

    def on(self):
        self.red.on()
        self.green.on()
        self.blue.on()

    def breeze_loop(self):
        print('Breeze mode on')
        lights = [self.red, self.green, self.blue]
        current_color = 0
        brightness = 0
        direction = 1
        while self.status['mode'] == 'breeze':
            brightness += 0.01 * direction
            if brightness >= 1.0:    # 亮度增加到1,开始减少亮度
                direction = -1
                brightness = 1.0
            elif brightness <= 0.0:  # 亮度减少到0,切换颜色,开始增加亮度
                direction = 1
                brightness = 0.0
                current_color = (current_color + 1) % 3
            lights[current_color].value = brightness # 设置当前颜色的亮度
            sleep(0.1/self.status['speed'])  # 根据速度调整延时
        print('Breeze mode off')


if __name__ == '__main__':
    r = RGB()
    Thread(target=r.breeze_loop).start()
