"""网页模块
"""
# 第三方库
from flask import Flask, render_template, Response, request, jsonify  # 导入Flask相关模块
import numpy as np
import cv2

# 标准库
from time import sleep


class WEBAPP():
    def __init__(self, camera=None):
        self.app = Flask(__name__)           # 创建Flask应用
        self.routes()                        # 路由注册
        self.camera = camera                 # 相机对象
        self.camera_on = True                # 摄像头开关状态
        self.last_frame = np.zeros((3, 4, 3), np.uint8) # 上一帧图像


    def run(self):
        self.app.run(host='0.0.0.0')


    def gen_frame(self):
        while True:
            if self.camera and self.camera_on:
                self.last_frame = self.camera.get_frame()
            jpeg = cv2.imencode('.jpg', self.last_frame)[1].tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
            sleep(1/24) # 控制帧率


    def routes(self):
        def index():
            return render_template('index.html')

        def stream():
            return Response(self.gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
        def facetrack():
            try:
                data = request.get_json()
                if data['enable'] == True:
                    print('开启人脸跟踪')
                else:
                    print('关闭人脸跟踪')
                return jsonify({'status': 'ok'})
            except Exception as e:
                print('facetrack接口异常:', e)
                return jsonify({'status': 'error', 'msg': str(e)}), 500
        
        def camera_switch():
            try:
                data = request.get_json()
                self.camera_on = bool(data.get('enable', True))
                print('摄像头开关:', '开启' if self.camera_on else '关闭')
                return jsonify({'status': 'ok'})
            except Exception as e:
                print('camera_switch接口异常:', e)
                return jsonify({'status': 'error', 'msg': str(e)}), 500

        self.app.add_url_rule('/', view_func=index)
        self.app.add_url_rule('/stream', view_func=stream)
        self.app.add_url_rule('/facetrack', view_func=facetrack, methods=['POST'])
        self.app.add_url_rule('/camera_switch', view_func=camera_switch, methods=['POST'])

# 测试代码
if __name__ == '__main__':
    from PiCamera import PiCamera

    picamera = PiCamera()
    web_camera = WEBCamera(picamera)
    web_camera.run()
    