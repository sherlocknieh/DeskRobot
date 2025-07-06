"""人脸追踪模块
"""

if __name__ != '__main__':
    
    from .API_Camera.FaceDetector import FaceDetector
    from .API_Camera.PiCamera import PiCamera
    from .EventBus import EventBus
    from .API_CAR.Servo import HeadServo
    from .API_CAR.Car import Car


from simple_pid import PID


import threading
import queue
import logging
from time import sleep
logger = logging.getLogger("人脸追踪") # 日志工具

WIDTH = 640
HEIGHT = 480

class FaceTrack(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name="人脸追踪")
        self.event_queue = queue.Queue()     # 事件队列
        self.event_bus = EventBus()          # 事件总线
        self.car = Car()                     # 小车接口
        self.head = HeadServo()              # 舵机接口
        self.pid_x = PID(0.004, 0.001, 0.0005, setpoint=0) # PID控制器
        self.pid_y = PID(0.005, 0.001, 0.005, setpoint=0)   # PID控制器
        self.pid_z = PID(3.0, 0.005, 0.005, setpoint=0)      # PID控制器
        self.trackloop_flag = threading.Event()  # 人脸追踪标志位
        self.rect = None                     # 人脸追踪矩形

        # 订阅消息
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        self.event_bus.subscribe("FACE_TRACK_ON", self.event_queue, self.name)
        self.event_bus.subscribe("FACE_TRACK_OFF", self.event_queue, self.name)
        self.event_bus.subscribe("FACE_RECT", self.event_queue, self.name)

    def trackloop(self):
        """人脸追踪循环"""
        from math import cos
        while True:
            self.trackloop_flag.wait()
            while self.trackloop_flag.is_set():
                dx, dy, dz = 0, 0, 0
                y0 = self.head.get_angle()

                if self.rect:
                    x,y,w,h = self.rect
                    cx = x + w/2
                    cy = y + h/2
                    dx = WIDTH/2 - cx
                    dy = cy - HEIGHT/2
                    dz = h/HEIGHT*cos(y0)

                if abs(dx) < 10:
                    dx = 0
                if abs(dy) < 15:
                    dy = 0
                if abs(dz) < 0.1:
                    dz = 0

                vx = self.pid_x(dx)
                vy = self.pid_y(dy)
                vz = self.pid_z(dz)

                #print(f"dx:{dx:.2f}, vx:{vx:.2f}")
                print(f"dz:{dz:.2f}, vz:{vz:.2f}")
                #print(f"dy:{dy:.2f}, vy:{vy:.2f}")

                self.head.set_angle(y0 + vy)
                self.car.steer(vx, 0)
                sleep(1/50)

    def run(self):
        threading.Thread(target=self.trackloop, daemon=True).start()
        while True:
            event = self.event_queue.get()   # 从事件队列获取事件 (没有事件则阻塞)
            if event['type'] == "EXIT":      # 接收到"EXIT"消息则停止线程
                self.stop()
                break
            elif event['type'] == "FACE_TRACK_ON":    # 接收到"FACE_TRACK_ON"消息
                self.trackloop_flag.set()
                logger.info("开启人脸追踪")
            elif event['type'] == "FACE_TRACK_OFF":   # 接收到"FACE_TRACK_OFF"消息
                self.trackloop_flag.clear()
                logger.info("关闭人脸追踪")
            elif event['type'] == "FACE_RECT":       # 接收到"FACE_RECT"消息
                self.rect = event['data']
        print(f"{self.name} 线程已停止")

    def stop(self):
        self.car.speed(0, 0)
        self.trackloop_flag.clear()


"""测试代码"""
if __name__ == '__main__':
    from API_Camera.FaceDetector import FaceDetector
    from API_Camera.PiCamera import PiCamera
    from EventBus import EventBus
    from API_CAR.Servo import HeadServo
    from API_CAR.Car import Car

    face_track = FaceTrack()
    detector = FaceDetector()
    cam = PiCamera()

    def rect_gen_loop():
        while True:
            frame = cam.get_frame()
            frame, rect = detector.detect(frame)
            face_track.rect = rect
            sleep(1/50)

    t = threading.Thread(target=rect_gen_loop, daemon=True)
    t.start()
    face_track.start()
    face_track.event_bus.publish("FACE_TRACK_ON")
    t.join()
