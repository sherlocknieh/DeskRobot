import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import asyncio

import adafruit_ssd1306
import board
import busio
import roboeyes

from src.DeskRobot.util.config import (
    OLED_I2C_ADDRESS,
    OLED_SCREEN_HEIGHT,
    OLED_SCREEN_WIDTH,
)


async def draw_roboeyes():
    try:
        rbe = roboeyes.RoboEyes(OLED_SCREEN_WIDTH, OLED_SCREEN_HEIGHT, 30)
        rbe.set_autoblinker(True, 3, 2)
        rbe.set_idle_mode(True, 3, 2)

        i2c = busio.I2C(board.SCL, board.SDA)
        oled = adafruit_ssd1306.SSD1306_I2C(
            OLED_SCREEN_WIDTH, OLED_SCREEN_HEIGHT, i2c, addr=OLED_I2C_ADDRESS
        )
        oled.fill(0)
        oled.show()

        while True:
            image = rbe.update()

            if image:
                oled.image(image)
                oled.show()
    except KeyboardInterrupt:
        print("Exiting...")
        return
    except Exception as e:
        print(f"Error: {e}")
        return
    finally:
        if hasattr(oled, "deinit"):
            oled.deinit()
        if hasattr(i2c, "deinit"):
            i2c.deinit()
        print("Resources cleaned up.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(draw_roboeyes())
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        loop.close()
