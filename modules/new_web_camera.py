"""网络摄像头模块
"""

# 自定义模块
if __name__ != '__main__':
    from .EventBus import EventBus
    from .API_Camera.PiCamera import PiCamera


# 第三方库
from flask import Flask, render_template, Response, jsonify  # 导入Flask相关模块
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
        self.rect = {"x": 0, "y": 0, "w": 640, "h": 480}

    def gen_frames(self):
        while True:
            frame, rect = self.cam.get_frame(face_detection=True)
            jpeg = cv2.imencode('.jpg', frame)[1].tobytes()  # type: ignore
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
            sleep(1/40) # 控制帧率

    def register_routes(self):
        def index():
            return render_template('camera.html')

        def stream():
            self.cam.start()
            return Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame') # type: ignore

        def shutdown():
            self.cam.stop()
            return jsonify({'status': 'camera stopped'})

        def capture():
            frame = self.cam.get_frame('jpeg')
            return Response(frame, mimetype='image/jpeg')

        self.app.add_url_rule('/', view_func=index)
        self.app.add_url_rule('/stream', view_func=stream)
        self.app.add_url_rule('/shutdown', view_func=shutdown, methods=['rectT'])
        self.app.add_url_rule('/capture', view_func=capture)

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

    def web_server(self):
        self.logger.info("启动网络服务")
        self.app.run(host='0.0.0.0', port=5000, debug=False)
        self.logger.info("网络服务已关闭")

    def stop(self):
        self.cam.stop()
        self.thread_flag.clear()
        self.logger.info(f"已停止事件监听")



"""测试代码
"""
if __name__ == '__main__':

    from API_Camera.PiCamera import PiCamera
    from EventBus import EventBus

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
    )

    test = WebCamera()
    print("测试开始")
    test.start()
    test.join()
    print("测试结束")


