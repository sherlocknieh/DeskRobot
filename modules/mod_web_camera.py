"""网络摄像头模块
"""

# 自定义模块
if __name__ != '__main__':
    from .EventBus import EventBus
    from .API_Camera.PiCamera import PiCamera


# 第三方库
from flask import Flask, render_template, Response, request, jsonify  # 导入Flask相关模块
import cv2


# 标准库
import queue
import threading
import logging
from time import sleep


class WebCamera(threading.Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self.name = "网络摄像头"              # 模块名称
        self.logger = logging.getLogger(self.name) # 日志工具
        self.event_queue = queue.Queue()     # 事件队列
        self.event_bus = EventBus()          # 事件总线
        self.cam = PiCamera()                # 相机接口
        self.app = Flask(__name__)           # Flask应用
        self.thread_flag = threading.Event() # 线程控制标志位
        self.register_routes()               # 路由注册统一入口
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)

        self.face_track_flag = False         # 人脸跟踪标志位
        self.camera_on = False               # 摄像头开启标志位
        self.client_count = 0                # 客户端连接数
        self.client_count_lock = threading.Lock()  # 新增：计数器锁

    def gen_frames(self):
        try:
            while True:
                frame, rect = self.cam.get_frame(self.face_track_flag)
                if self.face_track_flag:
                    self.event_bus.publish("NEW_FRAME", {"frame": frame, "rect": rect})
                jpeg = cv2.imencode('.jpg', frame)[1].tobytes()  # type: ignore
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
                sleep(1/32) # 控制帧率
        finally:
            with self.client_count_lock:
                self.client_count -= 1
                self.logger.info(f"客户端断开，当前连接数: {self.client_count}")

    def register_routes(self):
        def index():
            return render_template('camera.html')

        def stream():
            with self.client_count_lock:
                self.client_count += 1
                self.logger.info(f"客户端连接数: {self.client_count}")
            if not self.camera_on:
                self.cam.start()
                self.camera_on = True
            return Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame') # type: ignore

        def shutdown():
            if self.client_count == 0:
                self.cam.stop()
                self.camera_on = False
                return jsonify({'status': 'camera stopped'})
            else:
                return jsonify({'status': 'camera still running'})

        def capture():
            frame, rect = self.cam.get_frame()
            jpeg = cv2.imencode('.jpg', frame)[1].tobytes()  # type: ignore
            return Response(jpeg, mimetype='image/jpeg')
        
        def face_track():
            data = request.get_json()
            # 参数和状态检查
            if not self.camera_on:
                return jsonify({'status': 'camera is off'}), 400
            if not data or 'enable' not in data:
                return jsonify({'status': 'bad request'}), 400
            if data['enable'] == True:
                self.face_track_flag = True
                self.event_bus.publish("FACE_TRACK_ON")
                self.logger.info("人脸跟踪已开启")
            else:
                self.face_track_flag = False
                self.event_bus.publish("FACE_TRACK_OFF")
                self.logger.info("人脸跟踪已关闭")
            return jsonify({'status': 'face track updated'})

        def get_status():
            return jsonify({
                'camera_on': self.camera_on,
                'face_tracking': self.face_track_flag
            })

        self.app.add_url_rule('/', view_func=index)
        self.app.add_url_rule('/stream', view_func=stream)
        self.app.add_url_rule('/shutdown', view_func=shutdown, methods=['POST'])
        self.app.add_url_rule('/capture', view_func=capture)
        self.app.add_url_rule('/status', view_func=get_status)
        self.app.add_url_rule('/face_track', view_func=face_track, methods=['POST'])

    def web_server(self):
        self.logger.info("启动网络服务")
        self.app.secret_key = 'secret_key'
        self.app.run(host='0.0.0.0', port=5000, debug=False)
        self.logger.info("网络服务已关闭")

    def run(self):
        threading.Thread(target=self.web_server, name="网页服务", daemon=True).start()
        
        self.logger.info("开始事件监听")
        self.thread_flag.set()
        while self.thread_flag.is_set():
            event = self.event_queue.get()
            event_type = event["type"]
            self.logger.info(f"收到 {event_type} 消息")
            if event_type == "EXIT":
                self.stop()
                break
            else:
                self.logger.info(f"收到事件 {event['type']}")
        self.logger.info("网络摄像头已停止")

    def stop(self):
        self.cam.stop()
        self.thread_flag.clear()
        self.logger.info(f"已停止事件监听")


"""测试代码
"""
if __name__ == '__main__':

    from API_Camera.PiCamera import PiCamera
    from EventBus import EventBus

    test = WebCamera()
    print("测试开始")
    test.start()
    test.join()
    print("测试结束")


