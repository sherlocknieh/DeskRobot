if __name__ != '__main__':
    from .EventBus import EventBus
    from .API_CAR.Servo import HeadServo
    from .API_CAR.LED import RGB
    from .API_CAR.Car import Car


from queue import Queue
import threading
import logging


class CarControl(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name = "小车模块")
        self.logger = logging.getLogger(self.name)
        self.car = Car()                     # 车轮接口
        self.rgb = RGB(10, 9, 11)            # LED灯接口
        self.head = HeadServo()              # 头部舵机接口

        self.event_queue = Queue()
        self.event_bus = EventBus()
        self._stop_event = threading.Event()

        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        self.event_bus.subscribe("CAR_SPEED", self.event_queue, self.name)
        self.event_bus.subscribe("CAR_STEER", self.event_queue, self.name)
        self.event_bus.subscribe("HEAD_NOD", self.event_queue, self.name)
        self.event_bus.subscribe("HEAD_ANGLE", self.event_queue, self.name)
        self.event_bus.subscribe("LED_ON", self.event_queue, self.name)
        self.event_bus.subscribe("LED_OFF", self.event_queue, self.name)
        self.event_bus.subscribe("LED_FLASH", self.event_queue, self.name)
        self.event_bus.subscribe("LED_BREEZE", self.event_queue, self.name)


    def run(self):

        x,y,L,R = 0,0,0,0
        while not self._stop_event.is_set():
            event = self.event_queue.get()

            event_type = event.get("type")
            data = event.get("data", {})

            if event_type == "EXIT":
                self.stop()
                break
            elif event_type == "CAR_SPEED":
                L = data["L"]
                R = data["R"]
                self.car.speed(L, R)
            elif event_type == "CAR_STEER":
                x = data["x"]
                y = data["y"]
                self.car.steer(x, y)
            elif event_type == "HEAD_NOD":
                times = data["times"]
                self.head.nod(times)
            elif event_type == "HEAD_ANGLE":
                angle = data["angle"]
                self.head.set_angle(angle)
            elif event['type'] == "LED_OFF":    # 接收到"LED_OFF"消息
                self.rgb.off()
            elif event['type'] == "LED_ON":     # 接收到"LED_ON"消息
                data = event['data']            # 获取事件数据
                self.rgb.on()                   # 默认全部打开
                if data:                        # 如果存在数据则设置颜色
                    r=data.get("r",0)
                    g=data.get("g",0)
                    b=data.get("b",0)
                    self.rgb.on(r, g, b)        # 根据参数设置颜色
            elif event['type'] == "LED_FLASH":  # 接收到"LED_FLASH"消息
                speed = event['data'].get("speed", 1)   # 获取事件数据中的speed参数, 若不存在则默认为1
                self.rgb.flash(speed)
            
            elif event['type'] == "LED_BREEZE":  # 接收到"LED_BREEZE"消息
                speed = event['data'].get("speed", 1)   # 获取事件数据中的speed参数, 若不存在则默认为1
                self.rgb.breeze(speed)
        self.logger.info(f"{self.name} 已退出")

    def stop(self):
        self.car.speed(0, 0)
        self._stop_event.set()



if __name__ == '__main__':
    pass