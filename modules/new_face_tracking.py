"""人脸追踪模块
"""

if __name__ != '__main__':
    from .EventBus import EventBus
    from .API_Camera.PiCamera import PiCamera
    from .API_Servo.Servo import HeadServo
    from .API_Car.Car import Car


from simple_pid import PID
import cv2

import threading
import queue
import logging

WIDTH = 640.0
HEIGHT = 480.0

class FaceTrack(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.name = "人脸追踪"                # 模块名称
        self.event_queue = queue.Queue()     # 事件队列
        self.event_bus = EventBus()          # 事件总线
#        self.cam = PiCamera()                # 相机接口
        self.car = Car()                     # 小车接口
        self.head = HeadServo()              # 舵机接口
        self.trackloop_flag = threading.Event()  # 人脸追踪标志位
        self.logger = logging.getLogger(self.name) # 日志工具
        self.pid_x = PID(0.006, 0.001, 0.0005, setpoint=0)  # PID控制器
        self.pid_y = PID(0.05, 0.01, 0.001, setpoint=0)      # PID控制器
        self.pid_z = PID(0.006, 0.00, 0, setpoint=0)      # PID控制器

        self.frame = None                    # 当前帧图像

        # 订阅消息
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        self.event_bus.subscribe("FACE_TRACK_ON", self.event_queue, self.name)
        self.event_bus.subscribe("FACE_TRACK_OFF", self.event_queue, self.name)
        self.event_bus.subscribe("NEW_FRAME", self.event_queue, self.name)

    def trackloop(self):
        """
        人脸追踪循环
        """
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml") # type: ignore # 载入模型
        while True:
            self.trackloop_flag.wait()
            self.head.set_angle(32)
            while self.trackloop_flag.is_set():
                frame = self.frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)      # type: ignore
                faces = face_cascade.detectMultiScale(              # 人脸位置检测
                    gray,
                    scaleFactor=2,    # 图像缩放比例
                    minNeighbors=3,     # 检测敏感度（数值越大要求越严格）
                    minSize=(20, 20)    # 最小人脸尺寸
                )
                dx, dy, dz = 0.0, 0.0, 0.0
                if faces is not None and len(faces) > 0:
                    x,y,w,h = max(faces, key=lambda rect: rect[3])
                    cx = x + w/2
                    cy = y + h/2
                    dx = WIDTH/2 - cx
                    dy = cy - HEIGHT/2
                    dz = h - 150
                
                vx = self.pid_x(dx)
                vy = self.pid_y(dy)
                vz = self.pid_z(dz)

                if abs(dx) < 15:
                    vx = 0.0
                if abs(dy) < 8:
                    vy = 0.0
                y0 = self.head.get_angle()


                print(f"dz:{dz:.2f}, vz:{vz:.2f}")
                self.car.steer(vx, vz)
                self.head.set_angle(y0 + vy)
                
    

    def run(self):
        threading.Thread(target=self.trackloop, daemon=True).start()

        while True:
            event = self.event_queue.get()   # 从事件队列获取事件 (没有事件则阻塞)
            if event['type'] == "EXIT":      # 接收到"EXIT"消息则停止线程
                self.stop()
                break
            elif event['type'] == "FACE_TRACK_ON":    # 接收到"FACE_TRACK_ON"消息
                self.trackloop_flag.set()
                self.logger.info("开启人脸追踪")
            elif event['type'] == "FACE_TRACK_OFF":   # 接收到"FACE_TRACK_OFF"消息
                self.trackloop_flag.clear()
                self.logger.info("关闭人脸追踪")
            elif event['type'] == "NEW_FRAME":       # 接收到"NEW_FRAME"消息
                self.frame = event['data']["frame"]
                # 处理图像帧
        print(f"{self.name} 线程已停止")

    def stop(self):
        #self.cam.stop()
        self.car.speed(0, 0)
        self.trackloop_flag.clear()

"""测试代码:
"""

if __name__ == '__main__':
    
    from EventBus import EventBus
    from API_Servo.Servo import HeadServo
    from API_Car.Car import Car
    from time import sleep

    test = FaceTrack()

    print("测试开始")
    test.start()
    test.event_bus.publish("FACE_TRACK_ON")
    test.join()
    print("测试结束")
