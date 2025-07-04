"""网络摄像头模块
"""

# 自定义模块
if __name__ != '__main__':
    from .EventBus import EventBus
    from .API_Camera.PiCamera import PiCamera
    from .API_Camera.WEBAPP import WEBAPP


# 第三方库
from flask import Flask, render_template, Response, request, jsonify  # 导入Flask相关模块
import cv2


# 标准库
import queue
import threading
import logging
from time import sleep


class WEBCamera(threading.Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self.name = "网络摄像头"              # 模块名称
        self.logger = logging.getLogger(self.name) # 日志工具
        self.event_queue = queue.Queue()     # 事件队列
        self.event_bus = EventBus()          # 事件总线
        self.cam = PiCamera()                # 相机接口
        self.web = WEBAPP(self.cam)          # Flask应用
        self.thread_flag = threading.Event() # 线程控制标志位
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)

        self.face_track_flag = False         # 人脸跟踪标志位
        self.camera_on = False               # 摄像头开启标志位




    def run(self):
        self.web.run()
        
        self.logger.info("开始事件监听")
        self.thread_flag.set()
        while self.thread_flag.is_set():
            event = self.event_queue.get()
            event_type = event["type"]
            self.logger.info(f"收到 {event_type} 消息")
            if event_type == "EXIT":
                self.stop()
                break
            else:
                self.logger.info(f"收到事件 {event['type']}")
        self.logger.info("网络摄像头已停止")

    def stop(self):
        self.cam.stop()
        self.thread_flag.clear()
        self.logger.info(f"已停止事件监听")


"""测试代码
"""
if __name__ == '__main__':

    from API_Camera.PiCamera import PiCamera
    from modules.API_Camera.WEBAPP import WEBAPP
    from EventBus import EventBus

    test = WEBCamera()
    print("测试开始")
    test.start()
    test.join()
    print("测试结束")


