import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages') # 为 picamera2 引入系统库路径
from picamera2 import Picamera2
sys.path.pop(0)  # 导入 picamera2 后立即移除系统库路径，避免影响其他模块
import cv2
from flask import Flask, render_template, request, jsonify, Response  # 导入Flask相关模块



# 创建Flask应用实例
app = Flask(__name__)

# 路由：处理根URL的请求
@app.route('/')
def index():
    # 返回渲染后的index.html模板
    return render_template('camera.html')

# 路由：处理视频流请求
@app.route('/stream')
def stream():
    # 返回帧生成函数生成的视频流
    # mimetype指定响应的MIME类型为multipart，用于流式传输
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame') # 使用可迭代函数生成视频流

def gen_frames():
    # 打开摄像头
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))
    picam2.start()
    while True:
        # 捕获帧
        frame = picam2.capture_array()
        # 转换为BGR格式（Flask需要JPEG，OpenCV处理BGR）
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # 编码为JPEG
        ret, buffer = cv2.imencode('.jpg', frame_bgr)
        frame = buffer.tobytes()
        # 添加帧头尾标识符
        yield (b'--frame\r\n' 
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # 释放摄像头
    picam2.stop()

# 程序入口点
if __name__ == '__main__':
    # 启动Flask应用
    # debug=False 表示关闭调试模式，用于生产环境
    app.run(debug=True)