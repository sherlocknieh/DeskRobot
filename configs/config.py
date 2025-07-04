"""配置文件
"""

config = {}


# STT 服务商, 可选 'iflytek' 或 'siliconflow'
config["stt_provider"] = 'iflytek'


# 讯飞语音api, 在讯飞开放平台 (https://www.xfyun.cn/) 获取
config["iflytek_app_id"] = "c1eca680"
config["iflytek_api_key"] = "5dfe59ca36641de7dadc0948d7240f2b"
config["iflytek_api_secret"] = "MTZlMjExMGMxN2M4MTgyMjg3Y2E3MTlk"


# Siliconflow 语音合成 API, 在 Siliconflow 开放平台 (https://www.siliconflow.cn/) 获取
config["llm_model_name"] = "Qwen/Qwen3-32B"
config["llm_base_url"] = "https://api.siliconflow.cn/v1"
config["llm_api_key"] = "sk-xgpbdlulapwpsfnzbwoudyzarrzietkkujcajphkvewveykq"
config["siliconflow_api_key"] = "sk-xgpbdlulapwpsfnzbwoudyzarrzietkkujcajphkvewveykq"




# 日志系统配置
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(level=logging.INFO):
    """配置日志系统"""

    import os
    log_dir = "localfiles/logs"
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


