"""
远程音频服务器端程序
在Windows机器上运行，接收来自SSH会话的音频命令
"""

import base64
import json
import os
import socket
import sys
import tempfile
import threading
import wave

import numpy as np
import pyaudio


class RemoteAudioServer:
    """
    远程音频服务器类
    用于在Windows上运行并处理来自远程客户端的音频播放和录制请求
    """

    def __init__(self, host="localhost", port=12345):
        """
        初始化远程音频服务器

        Args:
            host: 服务器绑定地址，默认为localhost
            port: 服务器端口，默认为12345
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.audio = pyaudio.PyAudio()

    def start(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # 设置套接字超时
            self.running = True

            print(f"Remote Audio Server is running on {self.host}:{self.port}")
            print("Waiting for connections...")

            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"Connection from {addr}")

                    # 为每个客户端创建一个新线程
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:  # 捕获超时异常
                    continue  # 继续循环以检查 self.running 状态
                except Exception as e:
                    if self.running:  # 忽略停止服务器时的异常
                        print(f"Error accepting connection: {e}")

        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        self.audio.terminate()

    def handle_client(self, client_socket, addr):
        """
        处理客户端连接

        Args:
            client_socket: 客户端套接字
            addr: 客户端地址
        """
        try:
            while self.running:
                # 接收数据
                data = ""
                while True:
                    chunk = client_socket.recv(4096).decode()
                    if not chunk:
                        break
                    data += chunk
                    if "\n" in chunk:
                        break

                if not data:
                    break

                # 解析JSON请求
                request = json.loads(data)
                action = request.get("action")

                if action == "play":
                    # 播放音频
                    audio_data = base64.b64decode(request["data"])

                    # 保存为临时文件
                    with tempfile.NamedTemporaryFile(
                        suffix=".wav", delete=False
                    ) as temp:
                        temp_path = temp.name
                        temp.write(audio_data)

                    # 播放
                    success = self.play_audio_file(temp_path)

                    # 删除临时文件
                    os.unlink(temp_path)

                    # 发送响应
                    if success:
                        client_socket.sendall("OK".encode())
                    else:
                        client_socket.sendall("ERROR".encode())

                elif action == "record":
                    # 录制音频
                    duration = request.get("duration", 5)
                    sample_rate = request.get("sample_rate", 16000)
                    channels = request.get("channels", 1)

                    # 录制
                    audio_data = self.record_audio(duration, sample_rate, channels)

                    if audio_data is not None:
                        # 创建临时文件
                        with tempfile.NamedTemporaryFile(
                            suffix=".wav", delete=False
                        ) as temp:
                            temp_path = temp.name

                        # 保存为WAV
                        with wave.open(temp_path, "wb") as wf:
                            wf.setnchannels(channels)
                            wf.setsampwidth(2)  # 16位
                            wf.setframerate(sample_rate)
                            wf.writeframes(audio_data.tobytes())

                        # 读取文件内容
                        with open(temp_path, "rb") as f:
                            file_content = f.read()

                        # 删除临时文件
                        os.unlink(temp_path)

                        # 编码为base64并发送
                        audio_base64 = base64.b64encode(file_content).decode("utf-8")
                        response = {"status": "OK", "data": audio_base64}
                    else:
                        response = {
                            "status": "ERROR",
                            "message": "Failed to record audio",
                        }

                    # 发送响应
                    client_socket.sendall((json.dumps(response) + "\n").encode())

                else:
                    # 未知操作
                    response = {
                        "status": "ERROR",
                        "message": f"Unknown action: {action}",
                    }
                    client_socket.sendall((json.dumps(response) + "\n").encode())

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            client_socket.close()
            print(f"Connection from {addr} closed")

    def play_audio_file(self, file_path):
        """
        播放音频文件

        Args:
            file_path: 音频文件路径

        Returns:
            bool: 是否成功播放
        """
        try:
            # 使用PyAudio播放WAV文件
            with wave.open(file_path, "rb") as wf:
                # 打开输出流
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                )

                # 读取并播放数据
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)

                # 关闭流
                stream.stop_stream()
                stream.close()

            return True
        except Exception as e:
            print(f"Error playing audio file: {e}")
            return False

    def record_audio(self, duration=5, sample_rate=16000, channels=1):
        """
        录制音频

        Args:
            duration: 录制时长(秒)，默认5秒
            sample_rate: 采样率，默认16000
            channels: 声道数，默认1

        Returns:
            numpy.ndarray: 录制的音频数据
        """
        try:
            # 打开输入流
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=1024,
            )

            print(f"Recording for {duration} seconds...")

            # 录制
            frames = []
            for i in range(0, int(sample_rate / 1024 * duration)):
                data = stream.read(1024)
                frames.append(data)

            print("Finished recording")

            # 关闭流
            stream.stop_stream()
            stream.close()

            # 转换为numpy数组
            audio_data = np.frombuffer(b"".join(frames), dtype=np.int16)
            return audio_data
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None


if __name__ == "__main__":
    # 默认参数
    host = "localhost"
    port = 12345

    # 解析命令行参数
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    # 创建并启动服务器
    server = RemoteAudioServer(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.stop()
