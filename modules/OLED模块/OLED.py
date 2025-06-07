"""
OLED显示设备模块，用于初始化和控制OLED显示屏
"""


OLED_CV_SIMULATION = True
OLED_I2C_ADDRESS = 0x3C
OLED_SCREEN_WIDTH = 128
OLED_SCREEN_HEIGHT = 64


if OLED_CV_SIMULATION:
    import cv2
    import numpy as np
else:
    import adafruit_ssd1306
    import board
    import busio

# 全局单例实例
_instance = None


class OLEDDisplay:
    """
    OLED显示设备控制类
    负责OLED显示屏的初始化、显示和清理
    支持实际硬件和CV模拟两种模式
    实现为单例模式，确保全局只有一个显示设备实例
    """

    def __init__(self):
        """初始化OLED显示设备"""
        global _instance
        if _instance is not None:
            raise RuntimeError(
                "尝试创建OLEDDisplay的多个实例。请使用get_instance()方法获取实例。"
            )

        self.i2c = None
        self.oled = None
        _instance = self
        self.is_simulation = OLED_CV_SIMULATION

        # 如果不是模拟模式，初始化实际硬件
        if not self.is_simulation:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.oled = adafruit_ssd1306.SSD1306_I2C(
                OLED_SCREEN_WIDTH, OLED_SCREEN_HEIGHT, self.i2c, addr=OLED_I2C_ADDRESS
            )
            self.clear_display()

    @staticmethod
    def get_instance():
        """
        获取OLEDDisplay的单例实例

        Returns:
            OLEDDisplay: 单例实例
        """
        global _instance
        if _instance is None:
            _instance = OLEDDisplay()
        return _instance

    def __del__(self):
        """清理OLED显示设备"""
        self.clear_display()

    def clear_display(self):
        """清除显示"""
        if not self.is_simulation and self.oled:
            self.oled.fill(0)
            self.oled.show()

    def display_image(self, image):
        """
        显示图像

        Args:
            image: PIL图像对象
        """
        if image:
            if self.is_simulation:
                # CV模拟模式，将图像保存为文件
                cv_image = np.array(image)
                cv_image = cv_image * 255  # 将0/1图像转换为0/255
                cv_image = cv_image.astype(np.uint8)

                scale_factor = 4
                width = int(cv_image.shape[1] * scale_factor)
                height = int(cv_image.shape[0] * scale_factor)
                dim = (width, height)
                resized_cv_image = cv2.resize(
                    cv_image, dim, interpolation=cv2.INTER_NEAREST
                )
                # cv2.imshow("RoboEyes Animation Sequence", resized_cv_image)
                cv2.imwrite("roboeyes.png", resized_cv_image)
            else:
                # 实际硬件模式，显示到OLED
                if self.oled:
                    self.oled.image(image)
                    self.oled.show()