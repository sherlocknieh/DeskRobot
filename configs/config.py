"""
项目全局配置文件
"""

import os


# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 日志系统配置
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(level=logging.INFO):
    """配置日志系统"""

    log_dir = os.path.join(PROJECT_ROOT, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file_path = os.path.join(log_dir, "desk_robot.log")


    # 配置根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 移除所有现有的处理器，以避免重复日志
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)


    # 创建一个 RotatingFileHandler, 用于写入日志文件
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=5 * 1024 * 1024,   # 日志文件最大为 5MB
        backupCount=3,              # 保留3个备份文件
        encoding="utf-8"
    )
    file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] \t%(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


    # 创建一个 StreamHandler, 用于在控制台输出
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] \t%(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    logging.info("日志系统配置成功")

setup_logging() # 执行日志系统配置


# API_KEY 相关配置
try:
    from dotenv import load_dotenv
except ImportError:
    logging.warning("依赖缺失, 请安装: pip install python-dotenv")
    exit()

# 加载 .env 文件
dotenv_path = os.path.join(PROJECT_ROOT, 'configs/.env')
if os.path.exists(dotenv_path):
    logging.info("正在导入 API_KEY")
    load_dotenv(dotenv_path)
else:
    logging.warning("API_KEY 配置文件不存在: \"configs/.env\"; AI和语音相关模块将无法正常工作")


# ==============================================================================
# 全局配置字典
# ==============================================================================

config = {}

# ==============================================================================
# AI & STT & TTS 服务商配置
# ==============================================================================

# STT 服务商, 可选 'iflytek' 或 'siliconflow'
config["stt_provider"] = os.getenv("STT_PROVIDER", "siliconflow")

# --- 讯飞语音配置 (stt_provider = 'iflytek' 时使用) ---
config["iflytek_app_id"] = os.getenv("IFLYTEK_APP_ID")
config["iflytek_api_key"] = os.getenv("IFLYTEK_API_KEY")
config["iflytek_api_secret"] = os.getenv("IFLYTEK_API_SECRET")

# --- SiliconFlow 配置 (stt_provider = 'siliconflow' 时使用) ---
config["siliconflow_api_key"] = os.getenv("SILICONFLOW_API_KEY")

# LLM 服务商
config["llm_base_url"] = "https://api.siliconflow.cn/v1"
config["llm_api_key"] = os.getenv("LLM_API_KEY")
config["llm_model_name"] = "Qwen/Qwen3-32B"

# ==============================================================================
# 语音模块配置
# ==============================================================================
config["voice_sample_rate"] = 16000  # 采样率
config["voice_channels"] = 1  # 声道数
config["voice_vad_threshold"] = 0.5  # VAD 灵敏度
config["voice_frames_per_buffer"] = 512  # 音频帧大小
config["silero_vad_model_path"] = "~/.cache/torch/hub/snakers4_silero-vad_master"

# ==============================================================================
# OLED 屏幕配置
# ==============================================================================
config["oled_width"] = 128
config["oled_height"] = 64
config["oled_fps"] = 50
config["oled_i2c_address"] = 0x3C
config["oled_is_simulation"] = False

# ==============================================================================
# 文本渲染配置
# ==============================================================================
config["text_renderer_font_path"] = "wqy-microhei"
# ==============================================================================
# Roboeyes 表情配置
# ==============================================================================
config["roboeyes_frame_rate"] = 50
config["roboeyes_width"] = 128
config["roboeyes_height"] = 64

# ==============================================================================
# 思考动画配置
# ==============================================================================
config["thinking_animation_frame_rate"] = 20
