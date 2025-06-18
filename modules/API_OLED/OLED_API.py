"""
通用屏幕显示设备API

负责最底层的屏幕硬件初始化、控制和图像显示。
支持物理硬件和OpenCV模拟两种模式。
实现为单例模式，确保全局只有一个显示设备实例。
"""

import atexit
import logging
import time

from utils.config import config

# 根据配置决定是否导入硬件驱动
IS_SIMULATION = config.get("screen_cv_simulation", True)

if IS_SIMULATION:
    import cv2
    import numpy as np
else:
    try:
        import adafruit_ssd1306
        import board
        import busio
    except ImportError:
        IS_SIMULATION = True  # 驱动导入失败，强制切换到模拟模式
        import cv2
        import numpy as np

        logging.warning("Adafruit库未找到，OLED将强制在模拟模式下运行。")
        adafruit_ssd1306 = None


logger = logging.getLogger(__name__)


class OLED:
    """
    屏幕显示设备控制类。
    实现为单例模式，确保全局只有一个显示设备实例。
    """

    _instance = None
    scale_factor = 4  # 仅用于模拟模式下的窗口放大

    @staticmethod
    def get_instance():
        """获取OLED的单例实例"""
        if OLED._instance is None:
            OLED._instance = OLED()
        return OLED._instance

    def __init__(self):
        """初始化屏幕显示设备"""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.is_simulation = IS_SIMULATION
        self.width = config.get("screen_width")
        self.height = config.get("screen_height")
        self.i2c_address = config.get("screen_i2c_address")
        self.screen = None

        try:
            if not self.is_simulation:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                self.screen = adafruit_ssd1306.SSD1306_I2C(
                    self.width, self.height, self.i2c, addr=self.i2c_address
                )
                logger.info("OLED 硬件初始化成功。")
                self.clear_display()
            else:
                logger.info("OLED 正在以模拟模式运行。")
        except Exception as e:
            logger.error(f"OLED 硬件初始化失败: {e}", exc_info=True)
            logger.info("切换到模拟模式运行。")
            self.is_simulation = True

        self._initialized = True
        atexit.register(self.clear_display)

    def clear_display(self):
        """清除显示"""
        if not self.is_simulation and self.screen:
            self.screen.fill(0)
            self.screen.show()
        elif self.is_simulation:
            cv2.destroyAllWindows()

    def display_image(self, image):
        """
        显示图像

        Args:
            image: PIL图像对象
        """
        if image:
            try:
                if self.is_simulation:
                    cv_image = np.array(image.convert("L"))
                    width = int(cv_image.shape[1] * self.scale_factor)
                    height = int(cv_image.shape[0] * self.scale_factor)
                    dim = (width, height)
                    resized_cv_image = cv2.resize(
                        cv_image, dim, interpolation=cv2.INTER_NEAREST
                    )
                    cv2.imshow("OLED Simulation", resized_cv_image)
                    cv2.waitKey(1)
                else:
                    if self.screen:
                        self.screen.image(image.convert("1"))
                        self.screen.show()
            except Exception:
                logger.error("显示图像时发生错误", exc_info=True)


if __name__ == "__main__":
    import sys
    from os import path

    # 为了能导入项目根目录下的模块 (utils, modules)
    project_root = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(project_root)

    from PIL import Image, ImageDraw

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("--- OLED API 测试 ---")
    try:
        # 1. 获取实例
        oled = OLED.get_instance()
        logging.info(f"OLED已实例化。是否为模拟模式: {oled.is_simulation}")

        # 2. 创建一个测试图像 (带对角线的白色方框)
        logging.info("正在创建测试图像...")
        width = oled.width
        height = oled.height
        image = Image.new("L", (width, height))  # 'L' for 8-bit pixels, black and white
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width - 1, height - 1), outline=255, fill=0)
        draw.line((0, 0, width - 1, height - 1), fill=255)
        draw.line((0, height - 1, width - 1, 0), fill=255)
        logging.info("测试图像创建完毕。")

        # 3. 显示图像
        logging.info("正在显示图像... (将显示5秒)")
        oled.display_image(image)
        time.sleep(5)

        # 4. 清除屏幕
        logging.info("正在清除屏幕...")
        oled.clear_display()
        time.sleep(1)  # 等待窗口关闭
        logging.info("--- OLED API 测试结束 ---")

    except Exception as e:
        logging.error(f"OLED API 测试失败: {e}", exc_info=True)

    # 在模拟模式下，等待按键后退出
    if IS_SIMULATION:
        logging.info("模拟模式下，按任意键关闭窗口...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
