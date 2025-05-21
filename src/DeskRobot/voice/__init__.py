"""
实现voice模块所需的初始化文件
"""

from .piper_tts import get_piper_tts
from .voice_interface import get_voice_interface

__all__ = ["get_voice_interface", "get_piper_tts"]
