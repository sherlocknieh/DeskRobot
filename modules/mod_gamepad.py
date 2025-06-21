if __name__ == '__main__':
    from API_Car.Car_API import Car
else:
    from .API_Car.Car_API import Car

from .event_bus import EventBus
import threading
import evdev
from queue import Queue
from time import sleep


class Gamepad:
    def __init__(self):
        self.gamepad = None

    def connect_gamepad(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            print("手柄已连接:", device.name)
            if "xbox" in device.name.lower():
                return device
        return None

    def connect_gamepad_thread(self):
        """手柄重连线程"""
        self.gamepad = self.connect_gamepad()
        while not self.gamepad:
            self.gamepad = self.connect_gamepad()
            sleep(1)




class CarControl(threading.Thread):
    def __init__(self):
        super().__init__()

        self.car = Car()
        self.gamepad = Gamepad()
        self.event_queue = Queue()
        self.event_bus = EventBus()
        self.event_bus.subscribe("STOP_THREADS", self.event_queue, "小车控制模块")
        self.event_bus.subscribe("WHEEL", self.event_queue, "小车控制模块")
        self.event_bus.subscribe("CAR", self.event_queue, "小车控制模块")

        self.thread_flag = threading.Event()


    def run(self):
        self.thread_flag.set()
        while self.thread_flag.is_set():
            event = self.event_queue.get()
            event_type = event.get("type")
            event_data = event.get("data")

            if event_type == "STOP_THREADS":
                self.stop()
                break
            elif event_type == "WHEEL":
                L = float(event_data.get("L", 0))
                R = float(event_data.get("R", 0))
                self.car.speed(L, R)
            elif event_type == "CAR":
                x = float(event_data.get("x", 0))
                y = float(event_data.get("y", 0))
                self.car.steer(x, y)

    def stop(self):
        self.car.speed(0, 0)
        self.thread_flag.clear()


if __name__ == '__main__':
    pass