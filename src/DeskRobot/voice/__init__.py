"""
实现voice模块所需的初始化文件
"""

from .fast_whisper_stt import get_fast_whisper_stt
from .piper_tts import get_piper_tts
from .voice_interface import get_voice_interface
from .vosk_stt import get_vosk_stt

__all__ = [
    "get_voice_interface",
    "get_piper_tts",
    "get_vosk_stt",
    "get_fast_whisper_stt",
]
