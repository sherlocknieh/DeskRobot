from gpiozero import PWMLED
from threading import Thread
from time import sleep

class TrafficLight:
    def __init__(self, r_pin, g_pin, b_pin):

        # 引脚初始化
        self.red   = PWMLED(r_pin)
        self.green = PWMLED(g_pin)
        self.blue  = PWMLED(b_pin)
        # 初始状态
        self.red.off()
        self.green.off()
        self.blue.off()
        # 状态变量
        self.state = '常亮'
        self.red_state = 0
        self.green_state = 0
        self.blue_state = 0
        self.switch_speed = 1

    def 常亮(self):
        if self.state == '常亮':
            self.red.value = self.red_state
            self.green.value = self.green_state
            self.blue.value = self.blue_state

    
    def 轮流(self):
        while self.state == '轮流':
            self.red.on()
            self.green.off()
            self.blue.off()
            sleep(1/self.switch_speed)
            self.red.off()
            self.green.on()
            sleep(1/self.switch_speed)
            self.green.off()
            self.blue.on()
            sleep(1/self.switch_speed)
    
    def 呼吸(self):
        while self.state == '呼吸':
            self.red.blink()
            sleep(1/self.switch_speed)
            self.red.off()
            self.green.blink()
            sleep(1/self.switch_speed)
            self.green.off()
            self.blue.blink()
            sleep(1/self.switch_speed)
            self.blue.off()


    def update(self, data={}):
        while True:
            if not data:
                continue
            else:
                self.red.on()


if __name__ == '__main__':
    traffic_light = TrafficLight(13,19,26)
