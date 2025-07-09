if __name__ != '__main__':
    from .API_CAR.Car import Car
    from .API_CAR.LED import RGB
    from .API_CAR.Servo import HeadServo
    from .EventBus import EventBus


import threading
import evdev
from queue import Queue
from time import sleep
import logging
from itertools import cycle


logger = logging.getLogger("手柄模块")


class GamePad(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name="手柄模块")
        self.gamepad = None
        self.event_queue = Queue()
        self.event_bus = EventBus()

        self.car = Car()                     # 车轮接口
        self.head = HeadServo()              # 头部舵机接口
        self.led = RGB()

        self._gamepad_connected = threading.Event()
        self._gamepad_connecting = threading.Event()
        self._car_control_mode = threading.Event()
        
        self.x = 0
        self.y = 0
        self.z = 0
        self.firstpress = True
        self.modes = cycle(['CAR', 'MUSIC', 'LED'])
        self.mode = next(self.modes)
        logger.info(f"切换到 {self.mode} 模式")
        self._car_control_mode.set()

        self.摇杆精度 = 65535
        self.扳机精度 = 1023

        self.event_bus.subscribe("EXIT", self.event_queue, self.name)    # 订阅总线 "EXIT" 事件

    def run(self):

        threading.Thread(target=self._gamepad_connect_loop, daemon=True).start() # 启动手柄连接线程
        threading.Thread(target=self._gamepad_event_loop, daemon=True).start()   # 启动手柄事件线程
        threading.Thread(target=self._car_control_loop, daemon=True).start()     # 启动控制输出线程

        # 主循环: 事件总线监听
        while True:
            event = self.event_queue.get()
            if event['type'] == "EXIT":
                logger.info("收到EXIT事件，手柄模块退出")
                break
        logger.info("手柄模块已退出")


    def _car_control_loop(self):
        """控制循环"""
        while True:
            self._car_control_mode.wait()
            if self.mode == 'CAR':
                logger.debug(f"x={self.x}, y={self.y}")
                self.car.steer(self.x, self.y)  # 直接控制车轮转动
            sleep(1/40) # 控制输出频率


    def _gamepad_event_loop(self):
        """手柄事件循环"""
        while True:
            logger.debug("等待手柄连接...")
            self._gamepad_connected.wait()
            logger.debug("手柄已连接...")
            try:
                for event in self.gamepad.read_loop():  # type: ignore
                    if event.type == evdev.ecodes.EV_ABS:
                        # 左摇杆横轴
                        if event.code == 0:
                            self.x = event.value/self.摇杆精度*2-1
                        # 左摇杆纵轴
                        elif event.code == 1:
                            self.y = -event.value/self.摇杆精度*2+1
                        # 水平方向键
                        elif event.code == 16:
                            self.x = event.value
                            if self.mode == 'MUSIC':
                                if event.value == 1:
                                    self.event_bus.publish("NEXT_SONG", self.name)
                                elif event.value == -1:
                                    self.event_bus.publish("PREVIOUS_SONG", self.name)
                        # 竖直方向键
                        elif event.code == 17:
                            self.y = -event.value
                            if self.mode == 'MUSIC':
                                if event.value == 1:
                                    self.event_bus.publish("PAUSE_MUSIC", self.name)
                                elif event.value == -1:
                                    self.event_bus.publish("PLAY_MUSIC", self.name)
                        # 右扳机
                        elif event.code == 9:
                            self.z = -event.value/self.扳机精度
                            if self.mode == 'CAR':
                                angle = -self.z*90
                                self.head.set_angle(angle)
                        # 左扳机
                        elif event.code == 10:
                            self.z = event.value/self.扳机精度
                            if self.mode == 'CAR':
                                angle = -self.z*90
                                self.head.set_angle(angle)
                        # 右摇杆横轴
                        elif event.code == 2:
                            self.rx = event.value/self.摇杆精度*2-1
                        # 右摇杆纵轴
                        elif event.code == 5:
                            self.ry = -event.value/self.摇杆精度*2+1
                    elif event.type == evdev.ecodes.EV_KEY:
                        if event.code == 304:
                            if event.value == 1:
                                logger.info(f'A键按下')
                        if event.code == 305:
                            if event.value == 1:
                                logger.info(f'B键按下')
                        if event.code == 307:
                            if event.value == 1:
                                logger.info(f'X键按下')
                        if event.code == 308:
                            if event.value == 1:
                                logger.info(f'Y键按下')
                        if event.code == 310:
                            if event.value == 1:
                                logger.info(f'LB按下')
                        if event.code == 311:
                            if event.value == 1:
                                logger.info(f'RB按下')
                        if event.code == 314:
                            if event.value == 1:
                                logger.info(f'左选项键按下')
                                self.mode = next(self.modes)
                                logger.info(f"切换到 {self.mode} 模式")
                                if self.mode == 'CAR':
                                    self._car_control_mode.set()
                                else:
                                    self._car_control_mode.clear()
                        if event.code == 315:
                            if event.value == 1:
                                logger.info(f'右选项键按下')
                        if event.code == 317:
                            if event.value == 1:
                                logger.info(f'左摇杆按下')
                        if event.code == 318:
                            if event.value == 1:
                                logger.info(f'右摇杆按下')
                        if event.code == 167:
                            if event.value == 1:
                                logger.info(f'截图键按下')
            except Exception: 
                logger.info("手柄已断开, 正在尝试重连...")
                self.gamepad = None
                self._gamepad_connecting.set()
                self._gamepad_connected.clear()


    def _gamepad_connect_loop(self):
        """手柄连接任务循环"""
        while True:
            self.gamepad = self.gamepad_detector()
            if self.gamepad:    # 连接成功
                self._gamepad_connected.set()
                self._gamepad_connecting.clear()
                logger.debug("等待手柄断开...")
                self._gamepad_connecting.wait()
                logger.debug("手柄已断开...")
            sleep(2)


    def gamepad_detector(self):
        """手柄检测与连接"""
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if "xbox" in device.name.lower():
                self.摇杆精度 = 65535
                self.扳机精度 = 1023
                logger.info(f"手柄已连接: {device.name}")    
                return device
            elif device.name =="GameSir-Nova Lite":
                self.摇杆精度 = 255
                self.扳机精度 = 255
                logger.info(f"手柄已连接: {device.name}")
                return device
        return None


if __name__ == '__main__':
    from API_CAR.Car import Car
    from API_CAR.Servo import HeadServo
    from API_CAR.LED import RGB
    from EventBus import EventBus
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] [%(name)s] \t%(message)s",
    )
    
    pad = GamePad()
    pad.start()
    pad.join()