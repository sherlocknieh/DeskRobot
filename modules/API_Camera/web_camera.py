from flask import Flask, render_template, request, jsonify, Response  # 导入Flask相关模块
import cv2  # 导入OpenCV库，用于视频捕获和处理

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
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        exit()
    while True:
        # 读取帧
        ret, frame = cap.read()
        if not ret:
            print("无法读取帧")
            break
        else:
            # 将图像编码为JPEG格式
            ret, buffer = cv2.imencode('.jpg', frame)
            # 将图像数据转换为字节流格式
            frame = buffer.tobytes()
            # 添加帧头尾标识符
            yield (b'--frame\r\n' 
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # 释放摄像头
    cap.release()

# 程序入口点
if __name__ == '__main__':
    # 启动Flask应用
    # debug=False 表示关闭调试模式，用于生产环境
    app.run(debug=True)