from PIL import Image, ImageDraw, ImageFont


class TextRenderer:
    def __init__(self, font_path):
        self.font_path = font_path

    def font_loader(self, font_size):
        """Loads and returns a font object."""
        return ImageFont.truetype(self.font_path, font_size)

    def render_text(
        self,
        text,
        font_size,
        image_width,
        image_height,
        text_color=1,  # For monochrome: 1 = white, 0 = black
        bg_color=0,  # For monochrome: 0 = black, 1 = white
        padding=2,
        align="center",
        valign="center",
        wrap=True,
    ):
        """
        Renders text onto a monochrome image for SSD1306 OLED compatibility.
        """
        font = self.font_loader(font_size)
        # Create monochrome image (mode "1") for OLED compatibility
        image = Image.new("1", (image_width, image_height), bg_color)
        draw = ImageDraw.Draw(image)

        final_text = text
        if wrap:
            final_text = self._wrap_text(text, font, image_width - padding * 2)

        # Get bounding box of the whole text
        text_bbox = draw.textbbox((0, 0), final_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate position based on alignment
        if align == "center":
            x = (image_width - text_width) / 2
        elif align == "right":
            x = image_width - text_width - padding
        else:  # Default to left
            x = padding

        # Calculate vertical position based on valign
        if valign == "bottom":
            y = image_height - text_height - text_bbox[1] - padding
        elif valign == "top":
            y = padding - text_bbox[1]
        else:  # Default to center
            y = (image_height - text_height) / 2 - text_bbox[1]

        draw.text((x, y), final_text, font=font, fill=text_color, align=align)

        return image

    def get_multiline_text_size(self, text, font_size, max_width, padding=2):
        """Calculates the size of a text block after wrapping."""
        font = self.font_loader(font_size)
        wrapped_text = self._wrap_text(text, font, max_width - padding * 2)

        # Use a dummy image to get the bounding box
        dummy_image = Image.new("1", (1, 1), 0)
        dummy_draw = ImageDraw.Draw(dummy_image)
        bbox = dummy_draw.textbbox((0, 0), wrapped_text, font=font)

        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    def _wrap_text(self, text, font, max_width):
        """
        Wraps text to fit within a specified width.
        """
        if font.getlength(text) <= max_width:
            return text

        lines = []
        words = text.split(" ")
        current_line = ""
        for word in words:
            if font.getlength(current_line + " " + word) <= max_width:
                current_line += " " + word
            else:
                lines.append(current_line.strip())
                current_line = word
        lines.append(current_line.strip())

        # For languages without spaces like Chinese, we might need a character-by-character wrap
        if " " not in text:
            lines = []
            current_line = ""
            for char in text:
                if font.getlength(current_line + char) <= max_width:
                    current_line += char
                else:
                    lines.append(current_line)
                    current_line = char
            lines.append(current_line)

        return "\n".join(lines).strip()


if __name__ == "__main__":
    print("TextRenderer fixed for monochrome OLED displays (mode '1')")
