import sys
print("导入系统库 libcamera")
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from picamera2 import Picamera2
print("已导入 libcamera")
sys.path.pop(0)


import cv2
import numpy as np
import mediapipe as mp


class KalmanBoxTracker:
    """Kalman滤波器"""
    def __init__(self, init_state=None):
        # 位置: x, y, w, h, 速度: dx, dy, dw, dh
        self.kalman = cv2.KalmanFilter(8, 4)
        self.kalman.measurementMatrix = np.eye(4, 8, dtype=np.float32)
        self.kalman.transitionMatrix = np.eye(8, dtype=np.float32)
        dt = 1
        for i in range(4):
            self.kalman.transitionMatrix[i, i+4] = dt
        self.kalman.processNoiseCov = np.eye(8, dtype=np.float32) * 0.01
        self.kalman.measurementNoiseCov = np.eye(4, dtype=np.float32) * 1
        self.kalman.errorCovPost = np.eye(8, dtype=np.float32)
        # 初始状态
        if init_state is None:
            init_state = np.array([[320], [240], [0], [0], [0], [0], [0], [0]], dtype=np.float32)
        self.kalman.statePost = init_state

    def update(self, x, y, w, h):
        """输入观测值，返回平滑后的边界框"""
        self.kalman.predict()
        measurement = np.array([[np.float32(x)],
                                [np.float32(y)],
                                [np.float32(w)],
                                [np.float32(h)]])
        estimate = self.kalman.correct(measurement)
        sx, sy, sw, sh = estimate[:4].flatten()
        return int(sx), int(sy), int(sw), int(sh)

kalman_tracker = KalmanBoxTracker()


import threading


class PiCamera:
    _instance = None
    _lock = threading.Lock()
    def __new__(cls):
        """实现单例模式"""
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
            # 只初始化一次 FaceDetection 实例
            self._face_detector = mp.solutions.face_detection.FaceDetection(
                min_detection_confidence=0.2, # 置信度阈值
                model_selection=0
            )

    def face_detection(self, BGR_frame):
        """人脸检测"""
        x, y, w, h = 320, 240, 0, 0
        results = self._face_detector.process(cv2.cvtColor(BGR_frame, cv2.COLOR_BGR2RGB))
        if results.detections:
            for detection in results.detections:
                #绘制人脸边界框
                bbox = detection.location_data.relative_bounding_box
                ih, iw, _ = BGR_frame.shape
                x, y = int(bbox.xmin * iw), int(bbox.ymin * ih)
                w, h = int(bbox.width * iw), int(bbox.height * ih)
                x, y, w, h = kalman_tracker.update(x, y, w, h)
                cv2.rectangle(BGR_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return BGR_frame, (x, y, w, h)

    def get_frame(self, face_detection=False):
        """获取一帧图像
        """

        frame = self.picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # 转换为 cv2 所需的 BGR 格式
        
        if face_detection:
            frame, rect = self.face_detection(frame)
            return frame, rect
        else:
            return frame, None

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



def webtest():
    
    from flask import Flask, render_template, Response, jsonify  # 导入Flask相关模块
    from time import sleep

    app = Flask(__name__)
    cam = PiCamera()

    def register_routes():
        def index():
            return render_template('camera.html')

        def stream():
            cam.start()
            def gen_frames():
                while True:
                    frame, rect = cam.get_frame(face_detection=True)
                    jpeg = cv2.imencode('.jpg', frame)[1].tobytes()
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
                    sleep(1/30)
            return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame') # type: ignore

        def shutdown():
            cam.stop()
            return jsonify({'status': 'camera stopped'})

        def capture():
            frame, rect = cam.get_frame()
            jpeg = cv2.imencode('.jpg', frame)[1].tobytes() # type: ignore
            return Response(jpeg, mimetype='image/jpeg') # type: ignore

        app.add_url_rule('/', view_func=index)
        app.add_url_rule('/stream', view_func=stream)
        app.add_url_rule('/shutdown', view_func=shutdown, methods=['POST'])
        app.add_url_rule('/capture', view_func=capture)

    register_routes()

    app.run(host='0.0.0.0', port=5000, debug=False)

def localtest():
    cam = PiCamera()
    frame = cam.get_frame()
    print(frame.shape) # type: ignore
    print(frame[0][0])
    cv2.imwrite('frame.jpg', frame) # type: ignore
    cam.stop()
    
if __name__ == '__main__':
    webtest()