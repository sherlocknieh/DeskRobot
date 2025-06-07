from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep

class Motor:
    def __init__(self, in1, in2, pwm):
        self.in1 = DigitalOutputDevice(in1)
        self.in2 = DigitalOutputDevice(in2)
        self.pwm = PWMOutputDevice(pwm)
        self.pwm.on()
        self.in1.off()
        self.in2.off()

    def speed(self, speed):
        self.pwm.value = speed

    def forward(self):
        self.in1.on()
        self.in2.off()

    def backward(self):
        self.in1.off()
        self.in2.on()

    def brake(self):
        self.in1.on()
        self.in2.on()
    
class Car:
    def __init__(self):
        self.motorA = Motor(14, 15, 18)
        self.motorB = Motor(23, 24, 19)
    
    def forward(self):
        self.motorA.forward()
        self.motorB.forward()

    def backward(self):
        self.motorA.backward()
        self.motorB.backward()

    def stop(self):
        self.motorA.brake()
        self.motorB.brake()

def test():
    car = Car()
    car.speed(0.5)

    car.forward()
    sleep(1)
    car.backward()
    sleep(1)
    car.stop()

if __name__ == "__main__":
    test()