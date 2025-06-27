import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages') # 为 picamera2 添加系统库路径
from picamera2 import Picamera2
sys.path.pop(0)  # 导入 picamera2 后立即移除系统库路径，避免影响其他模块

from flask import Flask, render_template, Response
import cv2

class WebCameraServer:
    def __init__(self):
        self.app = Flask(__name__)
        self._register_routes()

    def _register_routes(self):
        @self.app.route('/')
        def index():
            return render_template('camera.html')

        @self.app.route('/stream')
        def stream():
            return Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def gen_frames(self):
        picam2 = Picamera2()
        picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))
        picam2.start()
        try:
            while True:
                frame = picam2.capture_array()
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                ret, buffer = cv2.imencode('.jpg', frame_bgr)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        finally:
            picam2.stop()

    def run(self, **kwargs):
        self.app.run(**kwargs)

if __name__ == '__main__':
    server = WebCameraServer()
    server.run(debug=False)