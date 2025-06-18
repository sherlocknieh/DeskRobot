if __name__ == '__main__':
    from LED.LED_API import RGB     # 直接运行时使用
    import modules.API_EventBus.event_bus as event_bus
else:
    from .LED.LED_API import RGB    # 从外部调用时使用
    from modules.API_EventBus import event_bus

import threading
import logging
import queue
from time import sleep

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
        self.event_bus.subscribe("LED", self.event_queue)

    def run(self):
        print("LED_Control is running...")
        while True:
            try:
                event = self.event_queue.get(timeout=1)
                if event["type"] == "on":
                    self.rgb.on(r=event["r"], g=event["g"], b=event["b"])
                elif event["type"] == "off":
                    self.rgb.off()
                elif event["type"] == "flash":
                    self.rgb.flash(speed=event["speed"])
                elif event["type"] == "breeze":
                    self.rgb.breeze(speed=event["speed"])
            except queue.Empty:
                pass

def test():
    print("test is running...")
    while True:
        cmd = input("请输入指令：")

           
if __name__ == '__main__':
    led_control = LED_Control(event_bus)
    led_control.start()
    
