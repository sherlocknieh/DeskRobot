if __name__ == '__main__':
    from API_LED.LED import RGB     # 直接运行时使用
    import modules.API_EventBus.event_bus as event_bus
else:
    from .API_LED.LED import RGB    # 从外部调用时使用
    from modules.API_EventBus import event_bus

import threading
import queue

"""LED 控制模块

从事件总线接收指令
根据指令控制LED灯的状态

"""

class LED_Control(threading.Thread):
    def __init__(self, event_bus):
        super().__init__(daemon=True, name="LED_Control_Thread")
        self.event_bus = event_bus
        self.rgb = RGB(10, 9, 11)
        self.event_queue = queue.Queue()
        self._stop_event = threading.Event()
        self.event_bus.subscribe("LED", self.event_queue)
        self.event_bus.subscribe("STOP_THREADS", self.event_queue)

    def run(self):
        #self.event_bus.publish("THREAD_STARTED", name=self.__class__.__name__)
        print("LED_Control is running...")
        while True:
            try:
                event = self.event_queue.get(timeout=1)
                if event['type'] == "STOP_THREADS":
                    break
                data = self.event_queue.get(timeout=1)['payload']
                if data["action"] == "on":
                    r=float(data["r"])
                    g=float(data["g"])
                    b=float(data["b"])
                    self.rgb.on(r, g, b)
                elif data["action"] == "off":
                    self.rgb.off()
                elif data["action"] == "flash":
                    if data.get("speed"):
                        self.rgb.flash(speed=data["speed"])
                    else:
                        self.rgb.flash()
                elif data["action"] == "breeze":
                    if data.get("speed"):
                        self.rgb.breeze(speed=data["speed"])
                    else:
                        self.rgb.breeze()
            except queue.Empty:
                pass

    def stop(self):
        self._stop_event.set()