"""
远程语音测试脚本 (Windows端)
请在Windows电脑上运行这个脚本，以便通过SSH使用Windows的音频设备

安装依赖:
- pip install pyaudio numpy
"""

import os
import sys

# 添加项目目录到路径
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

# 导入远程音频服务器
from remote_audio.remote_audio_server import RemoteAudioServer


def main():
    """启动远程音频服务器"""
    print("DeskRobot Remote Audio Server")
    print("============================")

    # 默认参数
    host = "0.0.0.0"
    port = 12345

    # 解析命令行参数
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    print(f"Starting server on {host}:{port}")
    print("Press Ctrl+C to stop")

    # 创建并启动服务器
    server = RemoteAudioServer(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
