"""
实现voice模块所需的初始化文件
"""

from .fast_whisper_stt import FastWhisperSTT
from .piper_tts import PiperTTS
from .voice_interface import get_voice_interface
from .vosk_stt import VoskSTT

__all__ = [
    "get_voice_interface",
    "PiperTTS",
    "VoskSTT",
    "FastWhisperSTT"
]
