"""
LED 控制模块:
从事件总线接收 'LED' 事件
根据事件内容切换 LED 灯状态

Subscribe:
- "LED": LED控制指令
    - payload格式:
    {
        "action": str,  # 动作类型："on", "off", "blink", "color"
        "r": int,       # 红色值 (0-255)（可选）
        "g": int,       # 绿色值 (0-255)（可选）
        "b": int,       # 蓝色值 (0-255)（可选）
        "speed": float  # 闪烁频率      （可选）
    }
- "STOP_THREADS": 线程终止指令

Publish:
- 无

"""

if __name__ == '__main__':
    from API_LED.LED import RGB     # 直接运行时本模块时使用相对路径导入
    from EventBus import event_bus
else:
    from modules.API_LED.LED import RGB    # 被外层模块导入时使用绝对路径
    from modules.EventBus import event_bus

import threading
import queue


class LED_Control(threading.Thread):
    def __init__(self, event_bus):
        super().__init__(daemon=True, name="LED_Control_Thread")
        self.event_bus = event_bus
        self.rgb = RGB(10, 9, 11)
        self.event_queue = queue.Queue()
        self._stop_event = threading.Event()
        self.event_bus.subscribe("STOP_THREADS", self.event_queue, "LED灯模块")
        self.event_bus.subscribe("LED", self.event_queue, "LED灯模块")

    def run(self):
        #self.event_bus.publish("THREAD_STARTED", name=self.__class__.__name__)
        print("LED_Control is running...")
        while True:
            try:
                event = self.event_queue.get(timeout=1)
                if event['type'] == "STOP_THREADS":
                    print("LED_Control received STOP_THREADS event, stopping...")
                    self.stop()
                    break
                data = event['payload']
                if data["action"] == "on":
                    self.rgb.on()
                    if data.get("r") and data.get("g") and data.get("b"):
                        r=float(data["r"])
                        g=float(data["g"])
                        b=float(data["b"])
                        print(f"LED_Control received RGB: {r}, {g}, {b}")
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
        print("LED_Control is stopping...")
        self._stop_event.set()
        print("LED_Control stopped.")

if __name__ == '__main__':
    from mod_terminal_io import IOThread
    io_thread = IOThread(event_bus)
    led_control = LED_Control(event_bus)
    io_thread.start()
    led_control.start()
    print("ALL THREADS STARTED")
    led_control.join()
    print("LED_Control thread stopped.")
    io_thread.join()
    print("ALL THREADS STOPPED")