from Car_API import Car
import pygame
import math


car = Car()
pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("未检测到手柄")
    exit()
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"已连接手柄: {joystick.get_name()}")
print("开始监听按键，按 Ctrl+C 退出")

x = 0
y = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0: #横轴 左-1 右+1
                x = +event.value
            if event.axis == 1: #纵轴 上-1 下+1
                y = -event.value
        if event.type == pygame.JOYHATMOTION:
            x = event.value[0]
            y = event.value[1]
        L = (y + x/3)/1.2
        R = (y - x/3)/1.2
        print(f"L: {L:2f}, R: {R:2f}")
        car.speed(L, R)