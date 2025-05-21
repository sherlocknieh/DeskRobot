import asyncio

import roboeyes
from config import (
    OLED_CV_SIMULATION,
    OLED_FRAMERATE,
    OLED_I2C_ADDRESS,
    OLED_SCREEN_HEIGHT,
    OLED_SCREEN_WIDTH,
    PROJECT_ROOT,
)

if OLED_CV_SIMULATION:
    import cv2
    import numpy as np
else:
    import adafruit_ssd1306
    import board
    import busio


async def run_roboeyes():
    try:
        rbe = roboeyes.RoboEyes(OLED_SCREEN_WIDTH, OLED_SCREEN_HEIGHT, OLED_FRAMERATE)
        rbe.set_autoblinker(True, 3, 2)
        rbe.set_idle_mode(True, 3, 2)

        if not OLED_CV_SIMULATION:
            i2c = busio.I2C(board.SCL, board.SDA)
            oled = adafruit_ssd1306.SSD1306_I2C(
                OLED_SCREEN_WIDTH, OLED_SCREEN_HEIGHT, i2c, addr=OLED_I2C_ADDRESS
            )
            oled.fill(0)
            oled.show()

        while True:
            image = rbe.update()
            if image:
                if OLED_CV_SIMULATION:
                    cv_image = np.array(image)
                    cv_image = cv_image * 255  # Convert 0/1 image to 0/255
                    cv_image = cv_image.astype(np.uint8)

                    scale_factor = 4
                    width = int(cv_image.shape[1] * scale_factor)
                    height = int(cv_image.shape[0] * scale_factor)
                    dim = (width, height)
                    resized_cv_image = cv2.resize(
                        cv_image, dim, interpolation=cv2.INTER_NEAREST
                    )
                    # cv2.imshow("RoboEyes Animation Sequence", resized_cv_image)
                    cv2.imwrite(PROJECT_ROOT + "/roboeyes.png", resized_cv_image)
                else:
                    oled.image(image)
                    oled.show()
    except KeyboardInterrupt:
        print("Exiting...")
        return
    except Exception as e:
        print(f"Error: {e}")
        return
    finally:
        if OLED_CV_SIMULATION:
            pass
        else:
            if hasattr(oled, "deinit"):
                oled.deinit()
            if hasattr(i2c, "deinit"):
                i2c.deinit()
            print("Resources cleaned up.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_roboeyes())
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        loop.close()
