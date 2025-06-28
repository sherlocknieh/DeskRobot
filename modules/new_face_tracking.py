"""人脸追踪模块
"""

import threading
import queue
import logging
import cv2


#方案一：使用 OpenCV 自带的 Haar Cascade（轻量、速度快）
import cv2

# # 加载模型
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# # 人脸检测
# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

# # 人脸追踪
# for (x, y, w, h) in faces:
#     cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
#     roi_gray = gray[y:y+h, x:x+w]
#     roi_color = frame[y:y+h, x:x+w]
#     # 进一步处理（如识别）
#     eyes = eye_cascade.detectMultiScale(roi_gray)
#     for (ex,ey,ew,eh) in eyes:
#         cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)


# 方案二：使用 Ultraface ONNX	5~10MB	实时检测，轻量部署	✅（更高准确率）
# pip install onnxruntime numpy opencv-python
import onnxruntime
import numpy as np
import cv2

# 加载模型
session = onnxruntime.InferenceSession("ultraface-RFB-320.onnx", providers=['CPUExecutionProvider'])

def preprocess(img):
    img_resized = cv2.resize(img, (320, 240))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    input_tensor = img_rgb.astype(np.float32).transpose(2, 0, 1)
    input_tensor = np.expand_dims(input_tensor, axis=0) / 255.0
    return input_tensor

def detect_faces(img):
    input_tensor = preprocess(img)
    outputs = session.run(None, {'input': input_tensor})
    # 模型输出格式依赖模型定义，需查看模型结构
    # 这里只是结构示意，实际输出可能包含 bbox + scores
    # 此处略，需要根据模型说明文档处理
    return outputs




if __name__ != '__main__':
    from .EventBus import EventBus
    from .API_Camera.PiCamera import PiCamera
    from .API_Servo.Servo import HeadServo
    from .API_Car.Car import Car


class FaceTrack(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.name = "人脸追踪"                # 模块名称
        self.event_queue = queue.Queue()     # 事件队列
        self.event_bus = EventBus()          # 事件总线
        self.cam = PiCamera()                # 相机接口
        self.car = Car()                     # 小车接口
        self.head = HeadServo()              # 舵机接口
        self.thread_flag = threading.Event()      # 线程控制标志位
        self.face_track_flag = threading.Event()  # 人脸追踪标志位
        self.logger = logging.getLogger(self.name) # 日志工具

        # 订阅消息
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        self.event_bus.subscribe("FACE_TRACK_ON", self.event_queue, self.name)
        self.event_bus.subscribe("FACE_TRACK_OFF", self.event_queue, self.name)


    def run(self):
        self.thread_flag.set()               # 线程标志位设为 True
        while self.thread_flag.is_set():     # 循环控制

            event = self.event_queue.get()   # 从事件队列获取事件 (没有事件则阻塞)

            if event['type'] == "EXIT":      # 接收到"EXIT"消息则停止线程
                self.stop()
                break

            elif event['type'] == "FACE_TRACK_ON":    # 接收到"FACE_TRACK_ON"消息
                self.face_track_flag.set()
                self.logger.info("开启人脸追踪")

            elif event['type'] == "FACE_TRACK_OFF":    # 接收到"FACE_TRACK_OFF"消息
                self.face_track_flag.clear()
                self.logger.info("关闭人脸追踪")


    def trackloop(self):
        """
        人脸追踪循环
        """
        while self.face_track_flag.is_set():
            frame = self.get_frame() # type: ignore
            face_center = detect_face(frame)
            if face_center:
                    dx = face_center.x - frame_center.x  # 左右偏移
                    dy = face_center.y - frame_center.y  # 上下偏移

                if abs(dx) > 阈值:
                    控制左右轮速度(dx)  # 向左/右旋转机器人

                if abs(dy) > 阈值:
                    控制舵机俯仰(dy)   # 调整摄像头上下视角

        face_x, face_y, face_w, face_h = detected_face

        if face_w < target_width - tolerance:
            forward()
        elif face_w > target_width + tolerance:
            backward()
        else:
            stop()

        TARGET_FACE_WIDTH = 120   # 你设定的“理想人脸宽度”，可调
        TOLERANCE = 15            # 宽容范围，防止机器人抖动

        # 检测到人脸时
        for (x, y, w, h) in faces:
            center = (x + w//2, y + h//2)
            
            # 距离控制逻辑
            if w < TARGET_FACE_WIDTH - TOLERANCE:
                move_forward()
            elif w > TARGET_FACE_WIDTH + TOLERANCE:
                move_backward()
            else:
                stop_movement()


    def stop(self):
        self.face_track_flag.clear()    # 停止人脸追踪
        self.thread_flag.clear()        # 停止线程
        self.logger.info(f"{self.name} 线程已停止")



"""测试代码:
"""

if __name__ == '__main__':

    from API_Camera.PiCamera import PiCamera
    from API_Servo.Servo import HeadServo
    from API_Car.Car import Car
    from EventBus import EventBus
    from time import sleep

    test = FaceTrack()
    print("测试开始")
    test.start()

    test.event_bus.publish("FACE_TRACK_ON")
    sleep(30)

    test.event_bus.publish("FACE_TRACK_OFF")
    sleep(4)

    test.event_bus.publish("EXIT")
    test.join()
    print("测试结束")
    