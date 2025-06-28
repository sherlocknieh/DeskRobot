if __name__ != '__main__':
    from .API_Car.Car import Car
    from .EventBus import EventBus


import threading
import evdev
from queue import Queue
from time import sleep
import logging


logger = logging.getLogger("手柄模块")


class GamePad(threading.Thread):
    def __init__(self):
        super().__init__()
        self.name = "手柄模块"
        self.gamepad = None
        self.event_queue = Queue()
        self.event_bus = EventBus()

        self.car = Car()

        self._gamepad_event_loop_flag = threading.Event()
        self._gamepad_connect_loop_flag = threading.Event()
        
        self.x = 0
        self.y = 0


    def run(self):
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)    # 订阅总线 "EXIT" 事件

        threading.Thread(target=self._gamepad_connect_loop, daemon=True).start() # 启动手柄连接线程
        threading.Thread(target=self._gamepad_event_loop, daemon=True).start()   # 启动手柄事件线程
        threading.Thread(target=self._control_loop, daemon=True).start()         # 启动控制输出线程

        # 主循环: 事件总线监听
        while True:
            event = self.event_queue.get()
            if event['type'] == "EXIT":
                logger.info("收到EXIT事件，手柄模块退出")
                break
        logger.info("手柄模块已退出")


    def _control_loop(self):
        """控制循环
        获取最新数据
        控制车轮转动
        """
        while True:
            x, y = self.x, self.y
            self.car.steer(x, y)
            sleep(0.02) # 控制频率


    def _gamepad_event_loop(self):
        """手柄事件循环
        """
        while True:
            self._gamepad_event_loop_flag.wait()
            try:
                for event in self.gamepad.read_loop():  # type: ignore
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
                        if event.code == 304:
                            if event.value == 1: logger.info(f'A键按下')
                            if event.value == 0: logger.info(f'A键放开')
            except Exception: 
                logger.info("手柄已断开")
                self._gamepad_connect_loop_flag.set()


    def _gamepad_connect_loop(self):
        """手柄重连循环
        """
        self.gamepad = self.gamepad_connector()
        while True:
            if not self.gamepad:
                logger.info("手柄未连接")
                self.gamepad = self.gamepad_connector()
            if self.gamepad:
                self._gamepad_event_loop_flag.set()
                self._gamepad_connect_loop_flag.wait()
            sleep(1)


    def gamepad_connector(self):
        """手柄检测与连接
        """
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if "xbox" in device.name.lower():
                logger.info(f"手柄已连接: {device.name}")    
                return device
        return None


if __name__ == '__main__':
    from API_Car.Car import Car
    from EventBus import EventBus
    pad = GamePad()
    pad.start()