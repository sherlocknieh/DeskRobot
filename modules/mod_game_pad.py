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
        self.firstpress = True


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
                        elif event.code == 9:
                            z = event.value/1023
                            logger.info(f'右扳机: {z}')
                        elif event.code == 10:
                            z = event.value/1023
                            logger.info(f'左扳机: {z}')
                            self.event_bus.publish("HEAD_ANGLE",{"angle": -z*90})
                        else:
                            logger.info(f'按键事件: {event.code}; 值: {event.value}')
                    elif event.type == evdev.ecodes.EV_KEY:
                        logger.info(f'按键事件: {event.code}; 值: {event.value}')
                        if event.code == 304:
                            if event.value == 1:
                                logger.info(f'A键按下')
                                if self.firstpress:
                                    print("开始播放")
                                    
                                    self.event_bus.publish("PLAY_MUSIC")
                                    self.firstpress = False
                                else:
                                    print("暂停播放")
                                    self.event_bus.publish("PAUSE_MUSIC")
                                    self.firstpress = True
                            if event.value == 0: logger.info(f'A键放开')
                        if event.code == 305:
                            if event.value == 1:
                                logger.info(f'B键按下')
                                print("停止播放")
                                self.event_bus.publish("STOP_MUSIC")
                            if event.value == 0: logger.info(f'B键放开')
                        if event.code == 307:
                            if event.value == 1:
                                logger.info(f'X键按下')
                                print("上一曲")
                                self.event_bus.publish("PREVIOUS_SONG")
                            if event.value == 0: logger.info(f'X键放开')
                        if event.code == 308:
                            if event.value == 1:
                                logger.info(f'Y键按下')
                                print("下一曲")
                                self.event_bus.publish("NEXT_SONG")
                            if event.value == 0: logger.info(f'Y键放开')
                        if event.code == 310:
                            if event.value == 1:
                                logger.info(f'LB按下')
                            if event.value == 0: logger.info(f'LB放开')
                        if event.code == 311:
                            if event.value == 1:
                                logger.info(f'RB按下')
                            if event.value == 0: logger.info(f'RB放开')
                        if event.code == 314:
                            if event.value == 1:
                                logger.info(f'左菜单键按下')
                            if event.value == 0: logger.info(f'左菜单键放开')
                        if event.code == 315:
                            if event.value == 1:
                                logger.info(f'右菜单键按下')
                            if event.value == 0: logger.info(f'右菜单键放开')
                        if event.code == 316:
                            if event.value == 1:
                                logger.info(f'HOME键按下')
                                self.event_bus.publish("EXIT")
                                break
                            if event.value == 0: logger.info(f'HOME键放开')
                        if event.code == 317:
                            if event.value == 1:
                                logger.info(f'左摇杆按下')
                        if event.code == 318:
                            if event.value == 1:
                                logger.info(f'右摇杆按下')
                        if event.code == 167:
                            if event.value == 1:
                                logger.info(f'截图键键按下')
                                if self.firstpress:
                                    print("开启人脸跟踪")
                                    self.event_bus.publish("FACE_TRACK_ON")
                                    self.firstpress = False
                                else:
                                     print("关闭人脸跟踪")
                                     self.event_bus.publish("FACE_TRACK_OFF")
                                     self.firstpress = True
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