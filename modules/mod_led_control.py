"""
LED 控制模块:
从事件总线接收 'LED' 事件
根据事件内容切换 LED 灯状态


接收的消息类型:
    "STOP_THREADS"  : 停止本模块所有线程
    "LED"           : 切换 LED 灯状态
"""

if __name__ == '__main__':
    from API_LED.LED import RGB      # 直接运行时本模块时使用相对路径导入
    from event_bus import EventBus
else:
    from .API_LED.LED import RGB     # 被外层模块导入时使用绝对路径
    from .event_bus import EventBus


import threading
import queue


class LEDControl(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)

        self.rgb = RGB(10, 9, 11)

        self.event_queue = queue.Queue()    # 创建事件队列
        self.event_bus = EventBus()         # 加载事件总线
        self.event_bus.subscribe("STOP_THREADS", self.event_queue, "LED灯模块")  # 订阅"STOP_THREADS"消息
        self.event_bus.subscribe("LED", self.event_queue, "LED灯模块")           # 订阅"LED"消息

        self.thread_flag = threading.Event()    # 用于控制自身线程的运行状态
        # 调用 is_set() 获取状态, 初始状态为 False
        # 调用 set() 设为 True
        # 调用 clear() 设为 False
        # 调用 wait() 阻塞线程, 直到被其它线程调用 set()

    def run(self):
        self.thread_flag.set()              # 线程标志位设为 True
        while self.thread_flag.is_set():     # 线程循环条件: thread_flag 状态为 True

            event = self.event_queue.get()   # 从事件队列获取事件(如果没有事件则阻塞在这里)
            if event['type'] == "STOP_THREADS":  # 接收到"STOP_THREADS"消息则停止本线程
                self.stop()
                break
            elif event['type'] == "LED":        # 接收到"LED"消息
                data = event['data']            # 获取事件数据
                """LED 事件数据格式:
                {
                    "led": "on" | "off" | "flash" | "breeze",
                    "r": 0.0-1.0,
                    "g": 0.0-1.0,
                    "b": 0.0-1.0,
                    "speed": 0.5~10
                }
                """
                if data["led"] == "on":      # 根据事件数据执行动作
                    self.rgb.on()
                    if data.get("r") and data.get("g") and data.get("b"):
                        r=float(data["r"])
                        g=float(data["g"])
                        b=float(data["b"])
                        self.rgb.on(r, g, b)
                elif data["led"] == "off":
                    self.rgb.off()
                elif data["led"] == "flash":
                    self.rgb.flash()
                    if data.get("speed"):
                        self.rgb.flash(speed=data["speed"])
                elif data["led"] == "breeze":
                    self.rgb.breeze()
                    if data.get("speed"):
                        self.rgb.breeze(speed=data["speed"])

    def stop(self):
        self.thread_flag.clear()    # 线程标志位设为 False, 停止线程

if __name__ == '__main__':

    """
    测试: 
        单独测试无法获取事件队列, 故没有效果
        需要在主程序中启用并配合其它模块测试
    """
    led_control = LEDControl()

    led_control.start()
    
    led_control.join()