'''
pip install pigpio
sudo pigpiod
'''

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory


class HeadServo:
    def __init__(self):
        self.servo = AngularServo(
            pin=17,
            pin_factory=PiGPIOFactory(),
            min_angle=-90,
            max_angle=90,
            min_pulse_width=0.0005,
            max_pulse_width=0.0025
        )

    def set_angle(self, angle):
        if angle < -85:
            angle = -85
        elif angle > 45:
            angle = 45
        self.servo.angle = angle


if __name__ == '__main__':
    head_servo = HeadServo()
    head_servo.set_angle(-45)