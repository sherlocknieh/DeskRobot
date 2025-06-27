if __name__ != '__main__':
    from .API_Car.Car_API import Car
    from .EventBus import EventBus


import threading
import evdev
from queue import Queue
from time import sleep
import time

import logging
logger = logging.getLogger("手柄模块")


class GamePad(threading.Thread):
    def __init__(self):
        super().__init__()
        self.car = Car()
        self.event_queue = Queue()
        self.event_bus = EventBus()
        self.thread_flag = threading.Event()
        self.event_bus.subscribe("EXIT", self.event_queue, "手柄模块")
        self.reconnect_event = threading.Event()
        self.reconnecting = False

        self.x = 0
        self.y = 0
        self.gamepad = self.connect_gamepad()
        self.listener_thread = None
        self.lock = threading.Lock()

    def run(self):
        interval = 0.02  # 20ms一次，约50Hz
        last_send = 0

        while True:
            try:
                event = self.event_queue.get_nowait()
                if event['type'] == "EXIT":
                    logger.info("收到EXIT事件，手柄模块退出")
                    break
            except Exception:
                pass  # 队列为空时继续

            if not self.gamepad:
                self.start_reconnect_thread()
                self.reconnect_event.wait()
                self.reconnect_event.clear()
                # 重连成功后启动监听线程
                self.start_listener_thread()
            # 确保监听线程已启动
            if not self.listener_thread or not self.listener_thread.is_alive():
                self.start_listener_thread()
            now = time.time()
            if now - last_send > interval:
                with self.lock:
                    x, y = self.x, self.y
                self.car.steer(x, y)
                last_send = now
            sleep(interval)

    def start_listener_thread(self):
        if self.listener_thread and self.listener_thread.is_alive():
            return
        self.listener_thread = threading.Thread(target=self.update_xy, daemon=True)
        self.listener_thread.start()

    def update_xy(self):
        try:
            for event in self.gamepad.read_loop():
                with self.lock:
                    if event.type == evdev.ecodes.EV_ABS:
                        if event.code == 0:
                            self.x = event.value/65535*2-1
                        elif event.code == 1:
                            self.y = -event.value/65535*2+1
                        elif event.code == 16:
                            self.x = event.value
                        elif event.code == 17:
                            self.y = -event.value
                    elif event.type == evdev.ecodes.EV_KEY:
                        logger.info(f'按键事件: {event.code}; 值: {event.value}')
        except Exception as e:
            logger.info(f"监听线程异常: {e}")
            self.gamepad = None  # 通知主线程断开

    def start_reconnect_thread(self):
        if not self.reconnecting:
            self.reconnecting = True
            threading.Thread(target=self.reconnect_thread, daemon=True).start()

    def reconnect_thread(self):
        while not self.gamepad:
            self.gamepad = self.connect_gamepad()
            if self.gamepad:
                self.reconnect_event.set()
                self.reconnecting = False
                break
            sleep(1)

    def connect_gamepad(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if "xbox" in device.name.lower():
                logger.info(f"手柄已连接: {device.name}")
                return device
        logger.info("未发现手柄")
        return None

if __name__ == '__main__':
    from API_Car.Car_API import Car
    from EventBus import EventBus
    pad = GamePad()
    pad.start()