import logging
import sys


def setup_logging(level=logging.INFO):
    """
    配置全局日志记录器。
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    logging.info("日志系统配置成功。")
