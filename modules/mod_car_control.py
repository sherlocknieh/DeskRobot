if __name__ == '__main__':
    from API_Car.Car_API import Car
else:
    from .API_Car.Car_API import Car


import threading
from queue import Queue
from evdev import InputDevice, list_devices


class Gamepad:
    def __init__(self, event_bus):
        self.gamepad = None

        self.event_bus = event_bus
        self.event_bus.subscribe("gamepad_event", self.handle_event)

    def connect_gamepad(self):
        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            if "xbox" in device.name.lower():
                return device
        return None

    def connect_gamepad_thread(self):
        """连接手柄设备线程"""
        self.gamepad = self.connect_gamepad()

    def handle_event(self, event):
        if event["type"] == "button":
            if event["button"] == "A":
                self.event_bus.publish("car_speed", {"L": 1, "R": 1})
            elif event["button"] == "B":
                self.event_bus.publish("car_speed", {"L": 0, "R": 0})

class CarControl(threading.Thread):
    def __init__(self, event_bus):
        super().__init__()
        self.car = Car()

        self.event_queue = Queue()
        self.event_bus = event_bus

        self.event_bus.subscribe("STOP_THREADS", self.event_queue)
        self.event_bus.subscribe("wheel", self.event_queue)
        self.event_bus.subscribe("car", self.event_queue)

        self._stop_event = threading.Event()


    def run(self):
        while not self._stop_event.is_set():
            try:
                event = self.event_queue.get_nowait()
                event_type = event.get("type")
                payload = event.get("payload", {})

                if event_type == "STOP_THREADS":
                    self.stop()
                    break
                elif event_type == "wheel":
                    L = float(payload.get("L", 0))
                    R = float(payload.get("R", 0))
                    self.car.speed(L, R)
                elif event_type == "car":
                    print("car event")
                    x = float(payload.get("x", 0))
                    y = float(payload.get("y", 0))
                    self.car.steer(x, y)
            except:
                pass

    def stop(self):
        self.car.speed(0, 0)
        self._stop_event.set()



if __name__ == '__main__':
    pass