from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep
import threading


class Wheel:
    def __init__(self, in1, in2, pwm):
        self.in1 = DigitalOutputDevice(in1)
        self.in2 = DigitalOutputDevice(in2)
        self.pwm = PWMOutputDevice(pwm)
        self.pwm.on()
        self.in1.off()
        self.in2.off()

    def backward(self):
        self.in1.on()
        self.in2.off()

    def forward(self):
        self.in1.off()
        self.in2.on()

    def speed(self, speed):
        if speed < 0:
            self.backward()
            speed = abs(speed)
        else:
            self.forward()
        if speed > 1:
            speed = 1
        self.pwm.value = speed


class Car:
    _instance = None
    _lock = threading.Lock()
    def __new__(cls):
        """实现单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        # 避免多次初始化
        if hasattr(self, 'A'):
            return
        self.A = Wheel(14, 15, 18)
        self.B = Wheel(23, 24, 19)
        self.STBY = DigitalOutputDevice(21)

        self.A.speed(0)
        self.B.speed(0)
        self.STBY.on()
    
    def speed(self, L, R):
        self.A.speed(L*1.13)
        self.B.speed(R)

    def steer(self, x, y):
        L = (y + x/(1+abs(2*y))) / 1.4
        R = (y - x/(1+abs(y))) / 1.4
        self.speed(L, R)

    def pause(self):
        self.STBY.off()
    
    def resume(self):
        self.STBY.on()

if __name__ == '__main__':
    car = Car()
    car.steer(0, 0.5)
    sleep(1)
    car.pause()
    sleep(1)
    car.resume()
    sleep(1)
    car.steer(0, 0)