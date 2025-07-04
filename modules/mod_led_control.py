"""LED 控制模块:

从事件总线接收事件
切换 LED 灯状态


接收的消息类型:
    "EXIT"  : 停止本模块所有线程
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


import threading
import queue
import logging


if __name__ != '__main__':
    from .API_LED.LED import RGB
    from .EventBus import EventBus


class LEDControl(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.name = "LED灯模块"           # 模块名称
        self.rgb = RGB(10, 9, 11)            # LED 接口
        self.event_queue = queue.Queue()     # 事件队列
        self.event_bus = EventBus()          # 事件总线
        self.thread_flag = threading.Event() # 线程控制标志位
        self.logger = logging.getLogger(self.name) # 日志工具
        self.rgb.on()  # 打开 LED 灯
        # 订阅消息
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        self.event_bus.subscribe("LED_ON", self.event_queue, self.name)
        self.event_bus.subscribe("LED_OFF", self.event_queue, self.name)
        self.event_bus.subscribe("LED_FLASH", self.event_queue, self.name)
        self.event_bus.subscribe("LED_BREEZE", self.event_queue, self.name)
        

    def run(self):
        self.thread_flag.set()              # 线程标志位设为 True
        while self.thread_flag.is_set():     # 线程循环条件: thread_flag 状态为 True

            event = self.event_queue.get()   # 从事件队列获取事件(如果没有事件则阻塞在这里)
            if event['type'] == "EXIT":  # 接收到"EXIT"消息则停止本线程
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
        self.logger.info("LED 控制模块已停止")
    
    def stop(self):
        self.thread_flag.clear()    # 线程标志位设为 False, 停止线程



"""测试代码:
"""

if __name__ == '__main__':

    from time import sleep
    from API_LED.LED import RGB
    from EventBus import EventBus


    led_control = LEDControl() # 创建 LED 控制线程
    print("LED 控制模块测试开始")
    led_control.start()        # 启动 LED 控制线程

    # 发送测试消息

    led_control.event_bus.publish("LED_ON")
    sleep(1)
    led_control.event_bus.publish("LED_OFF")
    sleep(1)
    led_control.event_bus.publish("EXIT")

    led_control.join()  # 等待子线程结束
    print("LED 控制模块测试结束")
    