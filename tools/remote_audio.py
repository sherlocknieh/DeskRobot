"""
远程音频转发模块，用于在远程开发时通过SSH使用本地Windows机器的音频设备
"""

import base64
import json
import os
import socket
import wave

import numpy as np


class RemoteAudioClient:
    """
    远程音频客户端类
    用于将音频数据发送到运行RemoteAudioServer的Windows机器上
    """

    def __init__(self, host="localhost", port=12345):
        """
        初始化远程音频客户端

        Args:
            host: 服务器主机地址，默认为localhost
            port: 服务器端口，默认为12345
        """
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self, max_retries=2, retry_delay=1.0):
        """
        连接到远程音频服务器，支持重试机制

        Args:
            max_retries: 最大重试次数，默认2次
            retry_delay: 重试间隔时间(秒)，默认1秒

        Returns:
            bool: 是否成功连接
        """
        print("正在连接到远程音频服务器...")

        # 清理主机名，确保没有URL前缀
        clean_host = self.host
        if clean_host.startswith(("http://", "https://")):
            clean_host = clean_host.split("//")[1]

        # 尝试连接，带重试机制
        for attempt in range(max_retries + 1):
            try:
                # 关闭之前的socket（如果有）
                if self.client_socket:
                    try:
                        self.client_socket.close()
                    except:
                        pass

                # 创建一个新的socket
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # 设置连接超时（3秒），避免无响应的连接阻塞太久
                self.client_socket.settimeout(3.0)

                # 尝试连接
                if attempt > 0:
                    print(f"尝试第 {attempt} 次重新连接到 {clean_host}:{self.port}...")
                else:
                    print(f"连接到 {clean_host}:{self.port}...")

                self.client_socket.connect((clean_host, self.port))

                # 连接成功后恢复为阻塞模式
                self.client_socket.settimeout(None)
                print(f"成功连接到远程音频服务器 {clean_host}:{self.port}")
                return True

            except socket.timeout:
                print("连接超时（3秒）")
            except socket.gaierror:
                print(f"无法解析主机名 '{clean_host}'")
                # 主机名解析错误通常不会通过重试解决
                break
            except ConnectionRefusedError:
                print(f"连接被拒绝，请确认服务器正在运行且端口 {self.port} 已开放")
            except Exception as e:
                print(f"连接失败: {e}")

            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries:
                print(f"将在 {retry_delay} 秒后重试...")
                import time

                time.sleep(retry_delay)

        print("无法连接到远程音频服务器，请检查网络连接和服务器状态")
        return False

    def play_audio(self, audio_data, sample_rate=16000, channels=1):
        """
        将音频数据发送到服务器进行播放，如果连接断开会尝试重连

        Args:
            audio_data: 音频数据(numpy array)
            sample_rate: 采样率，默认16000
            channels: 声道数，默认1

        Returns:
            bool: 是否成功播放
        """
        # 确保有连接，如果没有则尝试连接
        if not self.client_socket:
            if not self.connect():
                print("无法连接到远程音频服务器，无法播放音频")
                return False

        try:
            # 将numpy数组转换为bytes
            audio_bytes = audio_data.tobytes()

            # 创建一个临时的WAV文件
            temp_filename = f"temp_{os.getpid()}.wav"
            with wave.open(temp_filename, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 假设16位音频
                wf.setframerate(sample_rate)
                wf.writeframes(audio_bytes)

            # 读取并编码临时文件
            with open(temp_filename, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode("utf-8")

            # 删除临时文件
            try:
                os.remove(temp_filename)
            except Exception as e:
                print(f"警告: 无法删除临时文件 {temp_filename}: {e}")

            # 创建请求
            request = {"action": "play", "data": audio_base64}

            # 设置发送超时
            self.client_socket.settimeout(5.0)

            # 发送请求
            self.client_socket.sendall((json.dumps(request) + "\n").encode())
            response = self.client_socket.recv(1024).decode()

            # 恢复为默认模式
            self.client_socket.settimeout(None)

            return response == "OK"

        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            print("连接已断开，尝试重新连接...")
            if self.connect():
                # 重连成功，重试一次
                print("重新连接成功，重试播放音频...")
                return self.play_audio(audio_data, sample_rate, channels)
            return False

        except socket.timeout:
            print("发送音频数据超时")
            return False

        except Exception as e:
            print(f"播放音频时出错: {e}")
            return False

    def record_audio(self, duration=5, sample_rate=16000, channels=1):
        """
        请求服务器录制音频并返回，如果连接断开会尝试重连

        Args:
            duration: 录制时长(秒)，默认5秒
            sample_rate: 采样率，默认16000
            channels: 声道数，默认1

        Returns:
            numpy.ndarray: 录制的音频数据，如果出错则返回None
        """
        # 确保有连接，如果没有则尝试连接
        if not self.client_socket:
            if not self.connect():
                print("无法连接到远程音频服务器，无法录制音频")
                return None

        try:
            # 创建请求
            request = {
                "action": "record",
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": channels,
            }

            # 设置超时（录音时间 + 5秒缓冲）
            self.client_socket.settimeout(duration + 5.0)

            # 发送请求
            self.client_socket.sendall((json.dumps(request) + "\n").encode())

            # 接收音频数据
            response = ""
            while True:
                try:
                    chunk = self.client_socket.recv(4096).decode()
                    if not chunk:  # 连接关闭
                        raise ConnectionError("连接已关闭")
                    response += chunk
                    if "\n" in chunk:
                        break
                except socket.timeout:
                    print("接收音频数据超时，录制可能被中断")
                    break

            # 恢复为默认模式
            self.client_socket.settimeout(None)

            # 解析响应
            try:
                response_data = json.loads(response)
                if response_data["status"] == "OK":
                    audio_base64 = response_data["data"]
                    audio_bytes = base64.b64decode(audio_base64)

                    # 保存为临时文件（使用唯一文件名避免冲突）
                    temp_filename = f"temp_{os.getpid()}.wav"
                    with open(temp_filename, "wb") as f:
                        f.write(audio_bytes)

                    # 读取音频文件
                    with wave.open(temp_filename, "rb") as wf:
                        frames = wf.readframes(wf.getnframes())
                        audio_array = np.frombuffer(frames, dtype=np.int16)

                    # 删除临时文件
                    try:
                        os.remove(temp_filename)
                    except Exception as e:
                        print(f"警告: 无法删除临时文件 {temp_filename}: {e}")

                    return audio_array
                else:
                    print(f"录音失败: {response_data.get('message', '未知错误')}")
                    return None
            except json.JSONDecodeError:
                print("解析响应数据失败，收到的数据可能不完整")
                return None

        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            print("连接已断开，尝试重新连接...")
            if self.connect():
                # 重连成功，重试一次
                print("重新连接成功，重试录制音频...")
                return self.record_audio(duration, sample_rate, channels)
            return None

        except socket.timeout:
            print("录制音频超时")
            return None

        except Exception as e:
            print(f"录制音频时出错: {e}")
            return None

    def is_connected(self):
        """
        检查当前是否连接到服务器

        Returns:
            bool: 如果连接有效返回True，否则返回False
        """
        if not self.client_socket:
            return False

        try:
            # 尝试发送0字节数据来检查连接状态
            # 在某些环境中，这可能不适用，视情况调整
            self.client_socket.settimeout(0.5)
            self.client_socket.sendall(b"")
            return True
        except (socket.error, socket.timeout, OSError, ConnectionError) as e:
            # 捕获所有可能的连接相关错误
            print(f"连接状态检查失败: {e}")
            return False
        finally:
            # 恢复超时设置
            if self.client_socket:
                self.client_socket.settimeout(None)

    def close(self):
        """安全关闭连接"""
        if self.client_socket:
            try:
                # 尝试优雅关闭
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except (socket.error, OSError):
                # 这里不需要输出错误，因为在关闭一个已断开的socket时，通常会报错
                pass

            try:
                self.client_socket.close()
            except Exception as e:
                print(f"关闭socket时出错: {e}")

            self.client_socket = None
            print("远程音频连接已关闭")


# 单例模式
_instance = None


def get_remote_audio_client(host="localhost", port=12345):
    """
    获取RemoteAudioClient的单例实例

    Args:
        host: 服务器主机地址，默认为localhost
        port: 服务器端口，默认为12345

    Returns:
        RemoteAudioClient: 客户端实例
    """
    global _instance
    if _instance is None:
        _instance = RemoteAudioClient(host, port)
    return _instance


# 简单的测试
if __name__ == "__main__":
    client = get_remote_audio_client()

    # 测试录音
    print("Recording for 3 seconds...")
    audio = client.record_audio(duration=3)

    if audio is not None:
        print(f"Recorded audio shape: {audio.shape}")

        # 回放录音
        print("Playing back recorded audio...")
        client.play_audio(audio)

    client.close()
