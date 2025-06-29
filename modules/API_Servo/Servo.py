'''
pip install pigpio gpiozero
sudo pigpiod
'''

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

import time

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
        self.current_angle = 0

    def get_angle(self):
        return self.current_angle
    
    def set_angle(self, angle):
        """
            平视:   0 度
            仰视:  85 度
            低头: -45 度
        """
        if angle >  85:
            angle = 85
        elif angle < -45:
            angle = -45
        self.current_angle = angle
        self.servo.angle = -angle

    def nod(self, times=1, down_angle=-30, up_angle=32, delay=0.4):
        """
        点头
        """
        for _ in range(times):
            self.set_angle(down_angle)
            time.sleep(delay/2)
            self.set_angle(up_angle)
            time.sleep(delay)


if __name__ == '__main__':
    head_servo = HeadServo()
    head_servo.nod(times=2)  # 点头两次