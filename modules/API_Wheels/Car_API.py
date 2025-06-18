from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep

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
    def __init__(self):
        self.A = Wheel(14, 15, 18)
        self.B = Wheel(23, 24, 19)
        self.A.speed(0)
        self.B.speed(0)
    
    def speed(self, L, R):
        self.A.speed(R)
        self.B.speed(L)

if __name__ == '__main__':
    car = Car()
    car.speed(-0.6, -0.6)
    sleep(2)