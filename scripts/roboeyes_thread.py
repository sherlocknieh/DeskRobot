from config import SIMULATE_OLED,OLED_FRAMERATE, OLED_SCREEN_WIDTH, OLED_SCREEN_HEIGHT
from threading import Thread
from oledeyes.roboeyes import *

roboeyes = RoboEyes(OLED_SCREEN_WIDTH, OLED_SCREEN_HEIGHT, OLED_FRAMERATE)

if SIMULATE_OLED:
    import cv2
    import numpy as np
else:
    #!import luma.oled
    pass

def roboeyes_thread():
    """Run the RoboEyes in a separate thread."""
    roboeyes.set_autoblinker(True, 3, 2)
    roboeyes.set_idle_mode(True,3,2)
    while True:
        image = roboeyes.update()

        if SIMULATE_OLED:
                if image:
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
                    #cv2.imshow("RoboEyes Animation Sequence", resized_cv_image)
                    cv2.imwrite("roboeyes.png", resized_cv_image)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
        else:#device...
            pass

roboeyes_thread_instance = Thread(target=roboeyes_thread)

def run():
    """Run the RoboEyes in a separate thread."""
    # Start the RoboEyes in a separate thread
    roboeyes_thread_instance.start()
    print("RoboEyes started.")

def join():
    """Join the RoboEyes thread."""
    # Wait for the RoboEyes thread to finish
    roboeyes_thread_instance.join()
    print("RoboEyes stopped.")
