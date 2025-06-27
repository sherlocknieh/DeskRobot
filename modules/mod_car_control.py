if __name__ != '__main__':
    from .API_Car.Car_API import Car
    from .EventBus import EventBus


import threading
from queue import Queue


class CarControl(threading.Thread):
    def __init__(self):
        super().__init__()

        self.car = Car()
        self.event_queue = Queue()
        self.event_bus = EventBus()
        self.event_bus.subscribe("EXIT", self.event_queue, "小车控制模块")
        self.event_bus.subscribe("CAR_SPEED", self.event_queue, "小车控制模块")
        self.event_bus.subscribe("CAR_STEER", self.event_queue, "小车控制模块")

        self._stop_event = threading.Event()


    def run(self):
        while not self._stop_event.is_set():
            try:
                event = self.event_queue.get_nowait()
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
            except:
                pass

    def stop(self):
        self.car.speed(0, 0)
        self._stop_event.set()



if __name__ == '__main__':
    pass