

# 加载 OpenCV DNN 人脸检测模型
modelFile = cv2.data.haarcascades + "../dnn/face_detector/opencv_face_detector_uint8.pb"
configFile = cv2.data.haarcascades + "../dnn/face_detector/opencv_face_detector.pbtxt"
net = cv2.dnn.readNetFromTensorflow(modelFile, configFile)






"""人脸追踪模块
"""


import threading
import queue
import logging


if __name__ != '__main__':
    from .API_Camera.PiCamera import PiCameraModule
    from .API_Car.Car import Car
    from .API_Servo.Servo import HeadServo
    from .EventBus import EventBus




class FaceTrack(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.name = "人脸追踪"                # 模块名称
        self.thread_flag = threading.Event() # 线程控制标志位
        self.event_queue = queue.Queue()     # 事件队列
        self.event_bus = EventBus()          # 事件总线
        self.cam = PiCameraModule()          # 相机接口
        self.car = Car()                     # 小车接口
        self.head = HeadServo()              # 舵机接口
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



    
    def stop(self):
        self.thread_flag.clear()    # 线程标志位设为 False, 停止线程
        self.logger.info(f"{self.name} 已停止")



"""测试代码:
"""

if __name__ == '__main__':

    from API_Camera.PiCamera import PiCamera
    from API_Servo.Servo import HeadServo
    from API_Car.Car import Car
    from EventBus import EventBus
    from time import sleep

    test = FaceTrack()
    test.event_bus.publish("LED_ON")
    sleep(1)
    test.event_bus.publish("LED_OFF")
    sleep(1)
    test.event_bus.publish("EXIT")

    test.join()
    print("模块测试结束")
    