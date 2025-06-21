"""
OLED 动画 API
这是一个用于生成各种小动画帧的图形库。
它本身是无状态的，只根据传入的参数生成图像。
"""

import math

from PIL import Image, ImageDraw


class OledAnimationAPI:
    def __init__(self, width=128, height=64):
        self.width = width
        self.height = height

    def get_thinking_spinner_frame(
        self, frame_index: int, num_segments=8, line_length=10
    ) -> Image:
        """
        生成“思考中”旋转加载动画的单帧图像。

        Args:
            frame_index (int): 当前动画的帧序号。
            num_segments (int): 旋转动画的总段数（例如8个方向）。
            line_length (int): 加载线条的长度。

        Returns:
            Image: 一个包含单帧动画的Pillow图像对象。
        """
        # 创建一个全黑的透明背景图像
        image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 计算动画的中心点 (Y坐标上移12像素)
        center_x, center_y = self.width // 2, self.height // 2

        # 根据帧序号计算当前应该在哪一段
        segment = frame_index % num_segments

        # 计算当前段的角度
        angle = (360 / num_segments) * segment

        # 将角度转换为弧度
        rad = math.radians(angle)

        # 计算线条的终点坐标
        end_x = center_x + int(line_length * math.cos(rad))
        end_y = center_y + int(line_length * math.sin(rad))

        # 绘制线条，白色，宽度为2
        draw.line([(center_x, center_y), (end_x, end_y)], fill="white", width=2)

        # 为了在单色OLED上显示，需要转换图像模式
        # "1" 模式表示1位像素，黑白
        # 我们使用 "L" (luminance) 作为中间步骤，然后通过 point 转换为 "1"
        # 阈值128，意味着任何非纯黑的颜色都会变成白色
        return image.convert("L").point(lambda x: 255 if x > 128 else 0, mode="1")
