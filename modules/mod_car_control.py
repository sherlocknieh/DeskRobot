if __name__ != '__main__':
    from .EventBus import EventBus
    from .API_Car.Car import Car
    from .API_Servo.Servo import HeadServo


from queue import Queue
import threading
import logging


class CarControl(threading.Thread):
    def __init__(self):
        super().__init__()

        self.name = "运动控制"
        self.logger = logging.getLogger(self.name)
        self.car = Car()
        self.head_servo = HeadServo()
        self.event_queue = Queue()
        self.event_bus = EventBus()
        self._stop_event = threading.Event()


    def run(self):

        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        self.event_bus.subscribe("CAR_SPEED", self.event_queue, self.name)
        self.event_bus.subscribe("CAR_STEER", self.event_queue, self.name)
        self.event_bus.subscribe("HEAD_NOD", self.event_queue, self.name)
        self.event_bus.subscribe("HEAD_ANGLE", self.event_queue, self.name)

        while not self._stop_event.is_set():
            event = self.event_queue.get()

            event_type = event.get("type")
            data = event.get("data", {})

            if event_type == "EXIT":
                self.stop()
                break
            elif event_type == "CAR_SPEED":
                L = float(data.get("L", 0))
                R = float(data.get("R", 0))
                self.car.speed(L, R)
            elif event_type == "CAR_STEER":
                x = float(data.get("x", 0))
                y = float(data.get("y", 0))
                self.car.steer(x, y)
            elif event_type == "HEAD_NOD":
                times = int(data.get("times", 1))
                self.head_servo.nod(times)
            elif event_type == "HEAD_ANGLE":
                angle = int(data.get("angle", 0))
                self.head_servo.set_angle(angle)
        self.logger.info(f"{self.name} 线程退出")

    def stop(self):
        self.car.speed(0, 0)
        self._stop_event.set()



if __name__ == '__main__':
    pass