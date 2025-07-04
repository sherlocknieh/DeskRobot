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


class FaceDetector:

    def __init__(self, confidence=0.5):
        self._face_detector = mp.solutions.face_detection.FaceDetection( # type: ignore
            min_detection_confidence=confidence, # 置信度阈值
            model_selection=1                    # 0:短距离 1:长距离
        )

    def detect(self, frame):
        x, y, w, h = 320, 240, 0, 0
        results = self._face_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.detections:
            for detection in results.detections:
                #绘制人脸边界框
                bbox = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y = int(bbox.xmin * iw), int(bbox.ymin * ih)
                w, h = int(bbox.width * iw), int(bbox.height * ih)
                x, y, w, h = kalman_tracker.update(x, y, w, h)
        return (x, y, w, h)


if __name__ == '__main__':
    import threading
    from time import sleep
    from PiCamera import PiCamera
    from WEBAPP import WEBAPP
    cam = PiCamera()
    web = WEBAPP()
    app = FaceDetector()
    threading.Thread(target=web.run).start()
    while True:
        frame = cam.get_frame()
        rect = app.detect(frame)
        if rect is not None:
            x, y, w, h = rect
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        web.last_frame = frame
        sleep(0.02)