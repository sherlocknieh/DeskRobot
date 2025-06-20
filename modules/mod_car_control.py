if __name__ == '__main__':
    from API_Car.Car_API import Car
else:
    from .API_Car.Car_API import Car


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
    def __init__(self, event_bus):
        super().__init__()

        self.car = Car()
        self.gamepad = Gamepad()
        self.event_queue = Queue()

        self.event_bus = event_bus
        self.event_bus.subscribe("STOP_THREADS", self.event_queue, "小车控制模块")
        self.event_bus.subscribe("wheel", self.event_queue, "小车控制模块")
        self.event_bus.subscribe("car", self.event_queue, "小车控制模块")

        self._stop_event = threading.Event()
        # 初始状态为 False,
        # 调用 start() 设为 True,
        # 调用 clear() 设为 False
        # 调用 wait() 阻塞线程直到变为 True


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