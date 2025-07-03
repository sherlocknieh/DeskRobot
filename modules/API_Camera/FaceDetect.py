import cv2
import os
import requests
from tqdm import tqdm

from PiCamera import PiCamera

class FaceDetector:
    PROTO_URL = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
    MODEL_URL = "https://github.com/gopinath-balu/computer_vision/raw/refs/heads/master/CAFFE_DNN/res10_300x300_ssd_iter_140000.caffemodel"
    PROTO_PATH = "localfiles/deploy.prototxt"
    MODEL_PATH = "localfiles/res10_300x300_ssd_iter_140000.caffemodel"

    def __init__(self, confidence=0.6):
        self.confidence = confidence
        self._ensure_model()
        print("🚀 加载模型中...")
        self.net = cv2.dnn.readNetFromCaffe(self.PROTO_PATH, self.MODEL_PATH)
        self.cap = PiCamera()

    def _download_file(self, url, path):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
            with requests.get(url, headers=headers, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                progress = tqdm(
                    total=total_size, 
                    unit='B', 
                    unit_scale=True,
                    desc=f"下载 {os.path.basename(path)}",
                    bar_format="{l_bar}{bar:30}{r_bar}"
                )
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(len(chunk))
                progress.close()
        except Exception as e:
            print(f"\n❌ 下载失败: {str(e)}")

    def _ensure_model(self):
        if not os.path.exists(self.PROTO_PATH):
            self._download_file(self.PROTO_URL, self.PROTO_PATH)
        if not os.path.exists(self.MODEL_PATH):
            self._download_file(self.MODEL_URL, self.MODEL_PATH)

    def detect(self):
        while True:
            frame, rect = self.cap.get_frame()
            h, w = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
                                         (104.0, 177.0, 123.0))
            self.net.setInput(blob)
            detections = self.net.forward()

            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > self.confidence:
                    box = detections[0, 0, i, 3:7] * [w, h, w, h]
                    x1, y1, x2, y2 = box.astype("int")
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.imshow("Face Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = FaceDetector()
    detector.detect()