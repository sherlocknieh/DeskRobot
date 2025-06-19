"""
通用屏幕显示设备API

负责最底层的屏幕硬件初始化、控制和图像显示。
支持物理硬件和OpenCV模拟两种模式。
实现为单例模式，确保全局只有一个显示设备实例。
"""

import atexit
import logging
import time


logger = logging.getLogger(__name__)


class OLED:
    """
    屏幕显示设备控制类。
    实现为单例模式，确保全局只有一个显示设备实例。
    """

    _instance = None
    scale_factor = 4  # 仅用于模拟模式下的窗口放大
    is_simulation = False

    @staticmethod
    def get_instance(width=128, height=64, i2c_address=0x3C, is_simulation=False):
        """获取OLED的单例实例"""
        if OLED._instance is None:
            OLED._instance = OLED(  
                width=width,
                height=height,
                i2c_address=i2c_address,
                is_simulation=is_simulation
            )
        return OLED._instance
    
    def _import_dep(self):
        if self.is_simulation:  
            import cv2
            import numpy as np
            self.cv2 = cv2
            self.np = np
        else:
            try:
                import adafruit_ssd1306
                import board
                import busio
                self.adafruit_ssd1306 = adafruit_ssd1306
                self.board = board
                self.busio = busio
            except ImportError:
                self.is_simulation = True  # 驱动导入失败，强制切换到模拟模式
                import cv2
                import numpy as np
                self.cv2 = cv2
                self.np = np

                logging.warning("Adafruit库未找到，OLED将强制在模拟模式下运行。")
                self.adafruit_ssd1306 = None


    def __init__(self,width=128, height=64, i2c_address=0x3C, is_simulation=False):
        """初始化OLED显示设备"""
        """初始化屏幕显示设备"""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.is_simulation =  is_simulation
        self.width = width
        self.height = height
        self.i2c_address = i2c_address
        self.screen = None

        self._import_dep()

        try:
            if not self.is_simulation:
                self.i2c = self.busio.I2C(self.board.SCL, self.board.SDA)
                self.screen = self.adafruit_ssd1306.SSD1306_I2C(
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
            if hasattr(self, 'cv2'):
                self.cv2.destroyAllWindows()

    def display_image(self, image):
        """
        显示图像

        Args:
            image: PIL图像对象
        """
        if image:
            try:
                if self.is_simulation:
                    cv_image = self.np.array(image.convert("L"))
                    width = int(cv_image.shape[1] * self.scale_factor)
                    height = int(cv_image.shape[0] * self.scale_factor)
                    dim = (width, height)
                    resized_cv_image = self.cv2.resize(
                        cv_image, dim, interpolation=self.cv2.INTER_NEAREST
                    )
                    self.cv2.imshow("OLED Simulation", resized_cv_image)
                    self.cv2.waitKey(1)
                else:
                    if self.screen:
                        self.screen.image(image.convert("1"))
                        self.screen.show()
            except Exception:
                logger.error("显示图像时发生错误", exc_info=True)


if __name__ == "__main__":
    from PIL import Image, ImageDraw, ImageFont
    oled = OLED.get_instance()
    oled.clear_display()
    time.sleep(1)
    # 创建一个简单的图像
    image = Image.new("1", (oled.width, oled.height), 0)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((0, 0), "Hello, OLED!", font=font, fill=1)
    oled.display_image(image)
    time.sleep(2)
    oled.clear_display()