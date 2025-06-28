import sys
print("导入系统库 libcamera")
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from picamera2 import Picamera2
print("已导入 libcamera")
sys.path.pop(0)

import cv2
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
        print("正在加载摄像头")
        self.picam2 = Picamera2()
        print("正在配置摄像头")
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": resolution}))
        print("正在打开摄像头")
        self.picam2.start()
        print("摄像头已启动")
        self._running = True

    def get_frame(self, format='numpy'):
        """获取一帧图像
           可选格式: numpy, jpeg, png, stream
        """
        raw = self.picam2.capture_array()
        frame = cv2.cvtColor(raw, cv2.COLOR_RGB2BGR)
        if format == 'numpy':
            return frame
        elif format == 'jpeg':
            _, buf = cv2.imencode('.jpg', frame)
            return buf.tobytes()
        elif format == 'png':
            _, buf = cv2.imencode('.png', frame)
            return buf.tobytes()
        elif format == 'stream' :
            _, buf = cv2.imencode('.jpg', frame)
            return (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')
        else:
            raise ValueError("Unsupported format: {}".format(format))

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
    from flask import Flask, render_template, Response, jsonify  # 导入Flask相关模块

    app = Flask(__name__)
    cam = PiCamera()

    def register_routes():
        def index():
            return render_template('camera.html')

        def stream():
            cam.start()
            def gen_frames():
                while True:
                    frame = cam.get_frame('stream')
                    yield frame
            return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame') # type: ignore

        def shutdown():
            cam.stop()
            return jsonify({'status': 'camera stopped'})

        def capture():
            frame = cam.get_frame('jpeg')
            return Response(frame, mimetype='image/jpeg')

        app.add_url_rule('/', view_func=index)
        app.add_url_rule('/stream', view_func=stream)
        app.add_url_rule('/shutdown', view_func=shutdown, methods=['POST'])
        app.add_url_rule('/capture', view_func=capture)

    register_routes()

    app.run(host='0.0.0.0', port=5000, debug=False)