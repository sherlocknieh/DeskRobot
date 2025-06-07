detector = snowboydecoder.HotwordDetector("snowboy.umdl", sensitivity=0.6)
def wake_callback():
    play_beep()  # 提示音
detector.start(detected_callback=wake_callback)