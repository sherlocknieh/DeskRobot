"""配置日志系统"""

import os
import logging
from logging.handlers import RotatingFileHandler

# 获取根 logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 清空根 logger 的 handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)


# 创建一个 StreamHandler, 用于控制台输出
console_logger = logging.StreamHandler()
console_logger.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] \t%(message)s"))

root_logger.addHandler(console_logger)


# 创建一个 RotatingFileHandler, 用于写入日志文件
# 日志文件路径
log_file_path = 'localfiles/desk_robot.log'

file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=1024 * 1024,         # 日志文件最大为 1MB
    backupCount=2,
    encoding="utf-8"
)
file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] \t%(message)s")
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)



logger = logging.getLogger("DeskRobot")     # 日志工具
logger.info("日志系统已配置")