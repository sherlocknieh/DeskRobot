from PIL import Image

if __name__ == "__main__":
    from text_renderer import TextRenderer
else:
    from .text_renderer import TextRenderer


class TextScroller:
    def __init__(
        self,
        renderer: TextRenderer,
        text: str,
        font_size: int,
        viewport_width: int,
        viewport_height: int,
        scroll_direction: str = "horizontal",
        scroll_speed: int = 1,
        loop: bool = True,
    ):
        self.renderer = renderer
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.scroll_direction = scroll_direction
        self.scroll_speed = scroll_speed
        self.loop = loop
        self.finished = False

        if self.scroll_direction == "horizontal":
            self._init_horizontal(text, font_size)
        else:  # vertical
            self._init_vertical(text, font_size)

    def _init_horizontal(self, text, font_size):
        """Initializes the source image for horizontal scrolling."""
        temp_font = self.renderer.font_loader(font_size)
        text_width = int(temp_font.getlength(text))

        self.source_image = self.renderer.render_text(
            text,
            font_size,
            image_width=max(text_width + 20, self.viewport_width),
            image_height=self.viewport_height,
            align="left",
            wrap=False,  # No wrapping for horizontal scroll
        )
        self.source_width = self.source_image.width
        self.current_position_x = 0

    def _init_vertical(self, text, font_size):
        """Initializes the source image for vertical scrolling using precise height calculation."""
        # 1. Calculate the exact size of the wrapped text block
        # We use padding=0 here to get the raw text size, as render_text will handle its own padding.
        _w, actual_text_height = self.renderer.get_multiline_text_size(
            text, font_size, max_width=self.viewport_width, padding=0
        )

        # Add a small buffer if text height is smaller than viewport, to avoid empty scroll
        if 0 < actual_text_height < self.viewport_height:
            actual_text_height = self.viewport_height

        if actual_text_height == 0:  # Handle empty text
            self.source_image = Image.new(
                "RGB", (self.viewport_width, self.viewport_height)
            )
            self.finished = True
            return

        # 2. Render the text onto an image with the exact calculated height
        self.source_image = self.renderer.render_text(
            text,
            font_size,
            image_width=self.viewport_width,
            image_height=actual_text_height,
            align="left",
            valign="top",  # Crucial to avoid any vertical padding issues
            wrap=True,
            padding=0,  # Let the text start from the very top-left
        )
        self.source_height = self.source_image.height
        # 修复：让纵向滚动从下往上
        # 文本从视窗下方开始，向上移动进入视窗（从下往上滚动）
        self.current_position_y = self.viewport_height

    def next_frame(self):
        """Returns the next frame of the scrolling animation based on direction."""
        if self.finished:
            return None

        if self.scroll_direction == "horizontal":
            return self._next_horizontal_frame()
        else:
            return self._next_vertical_frame()

    def _next_horizontal_frame(self):
        """Calculates the next frame for horizontal scrolling."""
        left = self.current_position_x
        top = 0
        right = left + self.viewport_width
        bottom = self.viewport_height

        if right > self.source_image.width:
            if self.loop:
                frame = Image.new("RGB", (self.viewport_width, self.viewport_height))
                end_part_width = self.source_image.width - left
                end_part = self.source_image.crop(
                    (left, top, self.source_image.width, bottom)
                )
                frame.paste(end_part, (0, 0))

                remaining_width = self.viewport_width - end_part_width
                start_part = self.source_image.crop((0, top, remaining_width, bottom))
                frame.paste(start_part, (end_part_width, 0))

                self.current_position_x = (
                    self.current_position_x + self.scroll_speed
                ) % self.source_image.width
            else:
                self.finished = True
                return None
        else:
            frame = self.source_image.crop((left, top, right, bottom))
            self.current_position_x += self.scroll_speed
        return frame

    def _next_vertical_frame(self):
        """Calculates the next frame for vertical scrolling (bottom to top)."""
        # 创建一个视窗大小的帧，使用与源图像相同的模式
        frame = Image.new(
            self.source_image.mode, (self.viewport_width, self.viewport_height), 0
        )

        # 计算文本在帧中的位置（从下往上滚动）
        text_y = self.current_position_y

        # 如果文本还在视窗范围内
        if text_y > -self.source_height and text_y < self.viewport_height:
            # 计算需要裁剪的源图像区域
            src_top = max(0, -text_y)
            src_bottom = min(self.source_height, self.viewport_height - text_y)

            # 计算在帧中粘贴的位置
            dst_top = max(0, text_y)

            if src_top < src_bottom:
                # 裁剪源图像的可见部分
                visible_part = self.source_image.crop(
                    (0, src_top, self.viewport_width, src_bottom)
                )
                # 粘贴到帧中
                frame.paste(visible_part, (0, dst_top))

        # 更新位置：向上移动文本（从下往上滚动效果）
        self.current_position_y -= self.scroll_speed

        # 检查是否完成滚动
        if self.current_position_y <= -self.source_height:
            if self.loop:
                # 重置位置，重新开始滚动（从视窗底部重新开始）
                self.current_position_y = self.viewport_height
            else:
                self.finished = True
                return None

        return frame


if __name__ == "__main__":
    import os
    import sys

    import cv2
    import numpy as np

    # Add project root to path to allow importing config
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from configs.config import config

    def create_video(frames, output_path, fps, size):
        """Creates a video from a list of PIL Images."""
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, size)
        for frame in frames:
            # Convert PIL image to numpy array (OpenCV uses BGR format)
            frame_np = np.array(frame.convert("RGB"))
            video_writer.write(frame_np)
        video_writer.release()

    # 1. Initialize the renderer
    font_path = config.get("text_renderer_font_path")
    renderer = TextRenderer(font_path)

    # --- TEST 1: HORIZONTAL SCROLL ---
    text_to_scroll_h = (
        "This is a long horizontal scroll test. -- 这是一个横向滚动的测试。"
    )
    scroller_h = TextScroller(
        renderer,
        text_to_scroll_h,
        font_size=24,
        viewport_width=128,
        viewport_height=64,
        scroll_direction="horizontal",
        scroll_speed=2,
    )

    frames_h = []
    print("Generating horizontal animation frames for video...")
    for i in range(400):
        frame = scroller_h.next_frame()
        if frame:
            frames_h.append(frame)
        else:
            break
    create_video(frames_h, "scroll_animation_horizontal.mp4", 30, (128, 64))
    print("Horizontal test video created: scroll_animation_horizontal.mp4")

    # --- TEST 2: VERTICAL SCROLL (REFACTORED) ---
    text_to_scroll_v = "This is a refactored multi-line vertical scroll test. It should wrap automatically and scroll downwards from top to bottom without any black screen. -- 这是一个重构后的多行文本纵向滚动测试，它应该能自动换行并从上往下滚动，且不应出现任何黑屏。"
    scroller_v = TextScroller(
        renderer,
        text_to_scroll_v,
        font_size=16,
        viewport_width=128,
        viewport_height=64,
        scroll_direction="vertical",
        scroll_speed=1,  # Slower speed for better observation
        loop=True,
    )

    frames_v = []
    print("Generating vertical animation frames for video...")
    # Generate enough frames to see the full loop
    for i in range(scroller_v.source_height + scroller_v.viewport_height):
        frame = scroller_v.next_frame()
        if frame:
            frames_v.append(frame)
        else:
            break
    create_video(frames_v, "scroll_animation_vertical.mp4", 30, (128, 64))
    print("Vertical test video created: scroll_animation_vertical.mp4")

    print("\nAll tests complete. Check the generated .mp4 video files.")
