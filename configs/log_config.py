"""配置日志系统"""

import os
import logging
from logging.handlers import RotatingFileHandler

# 配置根 logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 移除所有现有的处理器，以避免重复日志
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)


# 创建一个 StreamHandler, 用于在控制台输出
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] \t%(message)s")
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)


# 创建一个 RotatingFileHandler, 用于写入日志文件

# 日志文件路径
log_dir = "localfiles/logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file_path = os.path.join(log_dir, "desk_robot.log")

file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=5 * 1024 * 1024,   # 日志文件最大为 5MB
    backupCount=3,              # 保留3个备份文件
    encoding="utf-8"
)
file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] \t%(message)s")
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

logging.info("\t日志系统配置成功")


logger = logging.getLogger("DeskRobot")     # 日志工具
