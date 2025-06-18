"""
语音接口模块，提供语音合成(TTS)和语音识别(STT)功能
支持本地和远程音频播放/录制
"""

import os
import sys
import wave

import numpy as np
from util.config import PROJECT_ROOT

from .STT.fast_whisper_stt import FastWhisperSTT
from .TTS.piper_tts import PiperTTS

# 导入远程音频客户端
try:
    from ...downloads.remote_audio import get_remote_audio_client
except ImportError:
    # 如果运行在本地，可能没有远程音频模块
    get_remote_audio_client = None


class VoiceInterface:
    """
    语音接口类，提供TTS和STT功能的抽象
    默认使用本地模式，可以通过设置环境变量切换到远程音频模式
    """

    def __init__(
        self, remote_host=None, remote_port=12345, sample_rate=16000, channels=1
    ):
        """
        初始化语音接口

        Args:
            remote_host: 远程音频服务器主机，如果为None则尝试从环境变量获取
            remote_port: 远程音频服务器端口，默认12345
        """
        # 检查是否使用远程音频
        self.remote_mode = False
        self.remote_client = None
        self.piper_tts = PiperTTS.get_instance()
        # self.vosk_stt = VoskSTT.get_instance()
        self.fast_whisper_stt = FastWhisperSTT.get_instance()
        self.sample_rate = sample_rate
        self.channels = channels

        # 如果没有指定remote_host，尝试从环境变量获取
        if remote_host is None:
            remote_host = os.environ.get("REMOTE_AUDIO_HOST")

        print(f"Remote audio host: {remote_host}")

        # 如果有remote_host，则使用远程模式
        if remote_host and get_remote_audio_client:
            try:
                self.remote_client = get_remote_audio_client(remote_host, remote_port)
                self.remote_mode = self.remote_client.connect()
                print(
                    f"Using remote audio mode: {'Connected' if self.remote_mode else 'Failed to connect'}"
                )
            except Exception as e:
                print(f"Failed to initialize remote audio client: {e}")
                self.remote_mode = False

        # 初始化本地音频库(如果需要)
        if not self.remote_mode:
            try:
                # 这里可以初始化本地音频库，如PyAudio等
                print("Using local audio mode (placeholder)")
            except Exception as e:
                print(f"Failed to initialize local audio: {e}")

    def text_to_speech(self, text, voice_id=None):
        """
        将文本转换为语音并播放

        Args:
            text: 要转换的文本
            voice_id: 语音ID，用于选择不同的声音
        """
        audio_path = self.piper_tts.text_to_speech(text)
        if audio_path is None:
            print("Failed to convert text to speech")
            return False
        audio_data, sample_rate, channels = self._load_audio_from_path(audio_path)
        # 播放音频
        self.play_audio(audio_data, sample_rate, channels)
        return True

    def speech_to_text(self, duration=5, save_audio=False):
        """
        录制语音并转换为文本

        Args:
            duration: 录制时长(秒)

        Returns:
            str: 识别的文本
        """
        print(f"Recording audio for {duration} seconds...")

        # 录制音频
        audio_data = self.record_audio(duration)

        if audio_data is None:
            return None
        if save_audio:
            audio_path = PROJECT_ROOT + "/tmp/recorded_audio.wav"
            self._save_audio_to_path(audio_data, audio_path)

        recognized_text = self.fast_whisper_stt.speech_to_text(audio=audio_path)

        print(f"Recognized text: '{recognized_text}'")
        return recognized_text

    def play_audio(self, audio_data, sample_rate=16000, channels=1):
        """
        播放音频数据

        Args:
            audio_data: 音频数据(numpy array)
            sample_rate: 采样率
            channels: 声道数

        Returns:
            bool: 是否成功播放
        """
        print("debug:", self.remote_mode, self.remote_client)
        if self.remote_mode and self.remote_client:
            return self.remote_client.play_audio(audio_data, sample_rate, channels)
        else:
            # 本地音频播放逻辑(占位符)
            print("Local audio playback (placeholder)")
            return True

    def record_audio(self, duration=5, sample_rate=16000, channels=1):
        """
        录制音频

        Args:
            duration: 录制时长(秒)
            sample_rate: 采样率
            channels: 声道数

        Returns:
            numpy.ndarray: 录制的音频数据
        """
        if self.remote_mode and self.remote_client:
            return self.remote_client.record_audio(duration, sample_rate, channels)
        else:
            # 本地音频录制逻辑(占位符)
            print("Local audio recording (placeholder)")
            # 创建一段静音数据用于测试
            return np.zeros(int(duration * sample_rate), dtype=np.int16)

    def close(self):
        """清理资源"""
        if self.remote_mode and self.remote_client:
            self.remote_client.close()

        # 清理本地资源

    def _load_audio_from_path(self, audio_path):
        """
        从指定的路径加载音频文件。

        Args:
            audio_path (str): 音频文件的路径。

        Returns:
            tuple: 包含 (audio_data, sample_rate, channels) 的元组，
                   如果加载失败则返回 (None, None, None)。
        """
        try:
            with wave.open(audio_path, "rb") as wf:
                params = wf.getparams()
                audio_data = np.frombuffer(
                    wf.readframes(params.nframes), dtype=np.int16
                )
                sample_rate = params.framerate
                channels = params.nchannels
                print(f"Audio params: {params}")
                print(f"Audio data shape: {audio_data.shape}")
                print(f"Sample rate: {sample_rate}, Channels: {channels}")
                return audio_data, sample_rate, channels
        except FileNotFoundError:
            print(f"Error: Audio file not found at {audio_path}")
            return None, None, None
        except Exception as e:
            print(f"Error loading audio from {audio_path}: {e}")
            return None, None, None

    def _save_audio_to_path(self, audio_data, audio_path):
        """
        将音频数据保存到指定路径。

        Args:
            audio_data (numpy.ndarray): 要保存的音频数据。
            audio_path (str): 保存音频文件的路径。
        """
        try:
            with wave.open(audio_path, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit PCM
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
                print(f"Audio saved to {audio_path}")

            return audio_path
        except Exception as e:
            print(f"Error saving audio to {audio_path}: {e}")


# 单例模式
_instance = None


def get_voice_interface(remote_host=None, remote_port=12345):
    """
    获取VoiceInterface的单例实例

    Args:
        remote_host: 远程音频服务器主机，如果为None则尝试从环境变量获取
        remote_port: 远程音频服务器端口，默认12345

    Returns:
        VoiceInterface: 语音接口实例
    """
    global _instance
    if _instance is None:
        _instance = VoiceInterface(remote_host, remote_port)
    return _instance


# 简单的测试
if __name__ == "__main__":
    # 设置远程主机(如果有)
    remote_host = None
    if len(sys.argv) > 1:
        remote_host = sys.argv[1]

    # 创建语音接口
    voice = get_voice_interface(remote_host)

    try:
        # 测试TTS
        voice.text_to_speech("你好，世界！")

        # 测试STT
        text = voice.speech_to_text(duration=3)
        if text:
            print(f"您说: {text}")
    finally:
        voice.close()
