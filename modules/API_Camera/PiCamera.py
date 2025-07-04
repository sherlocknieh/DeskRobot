import sys
print("正在导入系统库 libcamera")
sys.path.insert(0, '/usr/lib/python3/dist-packages')
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

    def __init__(self, resolution=(640, 480)):
        if not getattr(self, 'picam2', None):
            print("正在加载摄像头")
            self.picam2 = Picamera2()
            print("正在配置摄像头")
            self.picam2.configure(self.picam2.create_video_configuration(main={"size": resolution}))
            print("正在打开摄像头")
            self.picam2.start()
            print("摄像头已启动")
            self._running = True
 
    def get_frame(self):
        frame = self.picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # 转换为 cv2 使用的 BGR 格式
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



if __name__ == '__main__':
    from modules.API_Camera.WEBAPP import WEBCamera
    cam = PiCamera()
    web = WEBCamera(cam)
    web.run()