import logging
logger = logging.getLogger("PiCamera")

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
logger.info("正在导入 Picamera2...")
from picamera2 import Picamera2
sys.path.pop(0)

import cv2

import threading

class PiCamera:
    """单例模式"""
    _instance = None
    _lock = threading.Lock()
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not getattr(self, 'picam2', None):
            print("正在加载摄像头")
            self.picam2 = Picamera2()
            print("正在配置摄像头")
            video_config = self.picam2.create_video_configuration(
                buffer_count=3,
                main={"size": (640, 480), 'format': 'YUYV'},
            )
            self.picam2.configure(video_config)
            # print("配置详情")
            # from pprint import pprint
            # pprint(self.picam2.camera_config)
            print("正在打开摄像头")
            self.picam2.start()
            print("摄像头已启动")
            self._running = True
 
    def get_frame(self):
        frame = self.picam2.capture_array()
        #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # 转换为 cv2 使用的 BGR 格式
        frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_YUYV) # 转换为 cv2 使用的 BGR 格式
        return frame

    def start(self):
        if not self._running:
            self.picam2.start()
            print("摄像头已启动")
            self._running = True

    def stop(self):
        if self._running:
            self.picam2.stop()
            print("摄像头已关闭")
            self._running = False
