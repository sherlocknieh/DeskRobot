"""语音控制模块-本地版
"""


# 标准库
import queue
import threading
import logging
import re


# 第三方库
from jieba import posseg


# 自定义模块
if __name__ != '__main__':
    from .API_Camera.PiCamera import PiCamera
    from .API_Car.Car import Car
    from .API_Servo.Servo import HeadServo
    from .EventBus import EventBus


class VoiceControl(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.name = "语音控制"                # 模块名称
        self.event_queue = queue.Queue()     # 事件队列
        self.event_bus = EventBus()          # 事件总线
        self.cam = PiCamera()                # 相机接口
        self.car = Car()                     # 小车接口
        self.head = HeadServo()              # 舵机接口
        self.thread_flag = threading.Event() # 线程控制标志位
        self.face_track_flag = False         # 人脸追踪标志位
        self.logger = logging.getLogger(self.name) # 日志工具

        # 订阅消息
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        self.event_bus.subscribe("STT_RESULT_RECEIVED", self.event_queue, self.name)


    def run(self):
        self.thread_flag.set()               # 线程标志位设为 True
        while self.thread_flag.is_set():     # 循环控制

            event = self.event_queue.get()   # 从事件队列获取事件 (没有事件则阻塞)

            if event['type'] == "EXIT":      # 接收到"EXIT"消息则停止线程
                self.stop()
                break

                    


    def stop(self):
        self.thread_flag.clear()    # 线程标志位设为 False, 停止线程
        self.logger.info(f"{self.name} 已停止")



"""测试代码:
"""

if __name__ == '__main__':

    words = posseg.cut("打开灯123")
    for word, flag in words:
        print(f"{flag}: {word}")

    
    from API_Camera.PiCamera import PiCamera
    from API_Servo.Servo import HeadServo
    from API_Car.Car import Car
    from EventBus import EventBus
    from time import sleep

    test = VoiceCMD()
    print("测试开始")
    test.start()

    test.event_bus.publish("STT_RESULT_RECEIVED", {"text": "LED灯打开"})
    sleep(4)

    test.event_bus.publish("STT_RESULT_RECEIVED", {"text": "小车左转"})
    sleep(30)

    test.event_bus.publish("EXIT")
    test.join()
    print("测试结束")
    