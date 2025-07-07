

if __name__ != '__main__':
    from .API_Camera.PiCamera import PiCamera
    from .API_Camera.FaceDetector import FaceDetector
    from .EventBus import EventBus

from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import base64
import threading
import numpy as np

class WEBCamera(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name='WEBCamera')
        self.event_bus = EventBus()
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app)
        self.camera = PiCamera()
        self.detector = FaceDetector()
        self.client_count = 0

        self.camera_on = True
        self.face_tracking_on = False
        self.last_frame = np.zeros((480, 640, 3), np.uint8)
        self.register_routes()

    def register_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.socketio.on('connect')
        def handle_connect(auth=None):
            self.client_count += 1
            self.socketio.emit('client_count', self.client_count)
            print(f'客户端连接，当前在线：{self.client_count}')
            if self.client_count == 1:  # 只有在第一个客户端连接时启动视频流
                self.camera.start()
                self.camera_on = True
                self.socketio.start_background_task(self.stream_video)

        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.client_count -= 1
            self.socketio.emit('client_count', self.client_count)
            print(f'客户端断开，当前在线：{self.client_count}')
            if self.client_count == 0:  # 所有客户端断开时停止视频流
                self.camera.stop()
                self.camera_on = False

        
        @self.socketio.on('joystick')
        def handle_joystick(data):
            x = data.get('x', 0)  # 摇杆 X 轴（-1 到 1）
            y = data.get('y', 0)  # 摇杆 Y 轴（-1 到 1）
            #print(f'摇杆数据: X={x:.2f}, Y={y:.2f}')
            self.event_bus.publish('CAR_STEER', {'x': x, 'y': y}, self.name)
            
        @self.socketio.on('face_tracking_toggle')
        def handle_face_tracking_toggle(data):
            self.face_tracking_on = data.get('status', False)
            print(f'人脸跟踪已{"开启" if self.face_tracking_on else "关闭"}')
            if self.face_tracking_on:
                self.event_bus.publish('FACE_TRACK_ON', self.name)
            else:
                self.event_bus.publish('FACE_TRACK_OFF', self.name)

        @self.socketio.on('camera_toggle')
        def handle_camera_toggle(data):
            self.camera_on = data.get('status', False)
            print(f'摄像头已{"开启" if self.camera_on else "关闭"}')
            if self.camera_on:
                self.camera.start()
            else:
                self.camera.stop()

        @self.socketio.on('sliders')
        def handle_sliders(data):
            print(f'滑块数据: {data}')
            self.event_bus.publish('SLIDERS', data, self.name)
            

    def stream_video(self):
        while True:
            if self.camera_on:
                self.last_frame = self.camera.get_frame()
            else:
                self.last_frame = np.zeros((480, 640, 3), np.uint8)
            if self.face_tracking_on:
                self.last_frame, rect = self.detector.detect(self.last_frame)
                self.event_bus.publish('FACE_RECT', rect, self.name)
            JPEG = cv2.imencode('.jpg', self.last_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])[1]
            frame_base64 = base64.b64encode(JPEG).decode('utf-8')
            self.socketio.emit('video_frame', frame_base64)
            self.socketio.sleep(1/30)


    def run(self, host='0.0.0.0', port=5000):
        # import socket
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.connect(('8.8.8.8', 80))
        # ip = s.getsockname()[0]
        # s.close()
        # print(f"服务已启动: ")
        # print(f"\t访问地址: http://127.0.0.1:{port}")
        # print(f"\t访问地址: http://{ip}:{port}\n")
        self.socketio.run(self.app, host=host, port=port)


if __name__ == '__main__':
    from EventBus import EventBus
    from API_Camera.PiCamera import PiCamera
    from API_Camera.FaceDetector import FaceDetector
    server = WEBCamera()
    server.run()
