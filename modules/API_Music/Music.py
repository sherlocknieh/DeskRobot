import threading
import pygame
import time

def play_music(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)  # 避免 CPU 占用过高

# 启动播放线程
music_thread = threading.Thread(target=play_music, args=("music.mp3",), daemon=True)
music_thread.start()

# 主线程可以继续做其他事情
print("主线程继续运行...")
time.sleep(10)
