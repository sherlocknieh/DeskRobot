"""LED 控制模块:

从事件总线接收事件
切换 LED 灯状态


接收的消息类型:
    "STOP_THREADS"  : 停止本模块所有线程
    "LED_OFF"       : 关闭 LED 灯
    "LED_ON"        : 打开 LED 灯
        data = {
            "r": 0~1,
            "g": 0~1,
            "b": 0~1
        }
    "LED_FLASH"     : 闪烁 LED 灯
        data = {
            speed: 0.5~10
        }
    "LED_BREEZE"    : 呼吸 LED 灯
        data = {
            speed: 0.5~10
        }
"""


if __name__ == '__main__':
    from API_LED.LED import RGB      # 直接运行时本模块时使用相对路径导入
    from EventBus import EventBus
else:
    from .API_LED.LED import RGB     # 被外层模块导入时使用绝对路径
    from .EventBus import EventBus


import threading
import queue
import logging


logger = logging.getLogger("LED控制")    # 加载日志模块

# 
class LEDControl(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)

        self.rgb = RGB(10, 9, 11)

        self.event_queue = queue.Queue()    # 创建事件队列
        self.event_bus = EventBus()         # 加载事件总线
        
        # 订阅消息
        self.event_bus.subscribe("STOP_THREADS", self.event_queue, "LED灯模块")
        self.event_bus.subscribe("LED_ON", self.event_queue, "LED灯模块")
        self.event_bus.subscribe("LED_OFF", self.event_queue, "LED灯模块")
        self.event_bus.subscribe("LED_FLASH", self.event_queue, "LED灯模块")
        self.event_bus.subscribe("LED_BREEZE", self.event_queue, "LED灯模块")

        # 线程标志位 # 用于控制自身线程的运行状态
        self.thread_flag = threading.Event()
        # 调用 is_set() 获取状态, 初始状态为 False
        # 调用 set() 设为 True
        # 调用 clear() 设为 False
        # 调用 wait() 阻塞线程, 直到被其它线程用 set() 唤醒

    def run(self):
        self.thread_flag.set()              # 线程标志位设为 True
        while self.thread_flag.is_set():     # 线程循环条件: thread_flag 状态为 True

            event = self.event_queue.get()   # 从事件队列获取事件(如果没有事件则阻塞在这里)
            if event['type'] == "STOP_THREADS":  # 接收到"STOP_THREADS"消息则停止本线程
                self.stop()
                break

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
    
    def stop(self):
        logger.info("LED 控制模块已停止")
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