from gpiozero import PWMOutputDevice, OutputDevice
from time import sleep


class Car:
    def __init__(self):
        self.PWMA = PWMOutputDevice(18)
        self.PWMB = PWMOutputDevice(19)

        self.A1 = OutputDevice(14)
        self.A2 = OutputDevice(15)
        self.B1 = OutputDevice(23)
        self.B2 = OutputDevice(24)

        self.PWMA.on()
        self.PWMB.on()
    
    def speed(self, speed):
        self.PWMA.value = speed
        self.PWMB.value = speed

    def forward(self, distance=0):
        self.A1.on()
        self.A2.off()
        self.B1.on()
        self.B2.off()
        # self.motorA.forward()
        if distance > 0:
            sleep(distance/100)
            self.brake()

    def reverse(self, distance=0):
        self.A1.off()
        self.A2.on()
        self.B1.off()
        self.B2.on()
        # self.motorA.backward()
        # self.motorB.backward()
        if distance > 0:
            sleep(distance/100)
            self.brake()
        

    def brake(self):
        self.A1.on()
        self.A2.on()
        self.B1.on()
        self.B2.on()
    
    def stop(self):
        self.A1.off()
        self.A2.off()
        self.B1.off()
        self.B2.off()


def test():
    car = Car()
    car.speed(0.8)  # Set initial speed
    while True:
        cmd = input("Enter command: ")
        if cmd == "q":
            car.brake()
            break
        elif cmd == "f":
            car.forward()
        elif cmd == "b":
            car.reverse()
        elif cmd == "l":
            car.turn_left(90)
        elif cmd == "r":
            car.turn_right(90)
        elif cmd == "s":
            car.stop()
        else:
            print("Invalid command")

if __name__ == "__main__":
    test()