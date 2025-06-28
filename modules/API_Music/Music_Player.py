# pip install pygame


import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
music_path = os.path.join(project_root, "Creamy.ogg")


import pygame
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.mixer.music.load(music_path)
pygame.mixer.music.play()
input("按 Enter 停止...")
pygame.mixer.music.stop()