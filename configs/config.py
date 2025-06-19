"""
项目全局配置文件
"""

import os

import pyaudio
from dotenv import load_dotenv

# --- 基础路径配置 ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_PATH = os.path.join(PROJECT_ROOT, "downloads")

# --- 音频IO及VAD配置 ---
VAD_SAMPLE_RATE = 16000
config_data = {
    # PyAudio-related settings
    "pyaudio_rate": VAD_SAMPLE_RATE,
    "pyaudio_format": pyaudio.paInt16,
    "pyaudio_channels": 1,
    "vad_chunk_size": 512,  # VAD model requires 512, 1024, or 1536
    # VAD settings
    "vad_threshold": 0.45,
    "vad_min_silence_duration_ms": 700,
    "vad_speech_pad_ms": 300,
    # Device keywords for Windows
    "windows_input_device_keyword": "麦克风",
    "windows_output_device_keyword": "扬声器",
    # Snowboy Wake Word Engine
    "snowboy_sensitivity": 0.5,
    # OLED Screen
    "oled_is_simulation": True,
    "oled_i2c_address": 0x3C,
    "oled_width": 128,
    "oled_height": 64,
    # Roboeyes Animation
    "roboeyes_frame_rate": 50,  # 帧率
    "roboeyes_width": 128,
    "roboeyes_height": 64,
    # text rendering
    "text_renderer_font_path": os.path.join(PROJECT_ROOT, "fonts", "msyh.ttc"),
}

# --- 动态路径配置 ---
FFMPEG_PATH = os.path.join(DOWNLOADS_PATH, "ffmpeg")
PIPER_MODELS_PATH = os.path.join(DOWNLOADS_PATH, "piper-tts")
WHISPER_MODELS_PATH = os.path.join(DOWNLOADS_PATH, "fast-whisper")
VOSK_MODELS_PATH = os.path.join(DOWNLOADS_PATH, "vosk")
SNOWBOY_MODELS_PATH = os.path.join(DOWNLOADS_PATH, "snowboy")
EDGE_TTS_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "tmp", "edge_tts_output")

# --- URL及固定名称配置 ---
FFMPEG_URL_WINDOWS = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_URL_LINUX = {
    "amd64": "https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz",
    "arm64": "https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-arm64-static.tar.xz",
}
PIPER_VOICE_NAME = "zh_CN-huayan-medium"
PIPER_VOICE_URL = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/zh_CN/huayan/medium/{PIPER_VOICE_NAME}.onnx.json"
EDGE_TTS_VOICE = "zh-CN-XiaoxiaoNeural"
DOTENV_PATH = os.path.join(PROJECT_ROOT, "configs", ".env")

_config_instance = None


def get_config():
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


class Config:
    def __init__(self):
        load_dotenv(DOTENV_PATH)
        self._data = config_data.copy()
        # 将所有路径和URL也加入到配置字典中
        self._data["project_root"] = PROJECT_ROOT
        self._data["download_path"] = DOWNLOADS_PATH
        self._data["ffmpeg_path"] = FFMPEG_PATH
        self._data["ffmpeg_url_windows"] = FFMPEG_URL_WINDOWS
        self._data["ffmpeg_url_linux"] = FFMPEG_URL_LINUX
        self._data["piper_models_path"] = PIPER_MODELS_PATH
        self._data["piper_voice_name"] = PIPER_VOICE_NAME
        self._data["piper_voice_url"] = PIPER_VOICE_URL
        self._data["whisper_models_path"] = WHISPER_MODELS_PATH
        self._data["vosk_models_path"] = VOSK_MODELS_PATH
        self._data["snowboy_models_path"] = SNOWBOY_MODELS_PATH
        self._data["edge_tts_output_path"] = EDGE_TTS_OUTPUT_PATH
        self._data["edge_tts_voice"] = EDGE_TTS_VOICE
        self._data["dotenv_path"] = DOTENV_PATH
        self._data["llm_base_url"] = os.getenv("LLM_BASE_URL")
        self._data["llm_api_key"] = os.getenv("LLM_API_KEY")
        self._data["llm_model_name"] = os.getenv("LLM_MODEL_NAME")
        self._data["siliconflow_api_key"] = os.getenv("SILICONFLOW_API_KEY")

        # snowboy模型路径需要特殊处理
        self._data["snowboy_model_path"] = os.path.join(
            self._data["snowboy_models_path"], "snowboy.umdl"
        )

    def get(self, key, default=None):
        """获取配置项"""
        return self._data.get(key, default)

    def set(self, key, value):
        """设置配置项"""
        self._data[key] = value


config = get_config()
