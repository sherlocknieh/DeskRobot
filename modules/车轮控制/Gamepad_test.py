import pygame

pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("未检测到手柄")
    exit()
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"已连接手柄: {joystick.get_name()}")
print("开始监听按键，按 Ctrl+C 退出")

button_names = {
    0: "A",
    1: "B",

    3: "X",
    4: "Y",

    6: "LB",
    7: "RB",

    10: "VIEW",
    11: "MENU",

    12: "HOME",
    15: "SHARE",

    13: "左摇杆",
    14: "右摇杆",
}

axis_names = {
    0: "左摇杆-左右", # 左-1.0 右+1.0
    1: "左摇杆-上下", # 上-1.0 下+1.0

    2: "右摇杆-左右", # 左-1.0 右+1.0
    3: "右摇杆-上下", # 上-1.0 下+1.0

    5: "左扳机", # 放松-1.0 压紧+1.0
    4: "右扳机", # 放松-1.0 压紧+1.0
}

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                #print(f"按钮 {event.button} 按下")
                print(f"按钮 {button_names[event.button]} 按下")
            elif event.type == pygame.JOYBUTTONUP:
                #print(f"按钮 {event.button} 松开")
                print(f"按钮 {button_names[event.button]} 松开")
            elif event.type == pygame.JOYAXISMOTION:
                print(f"{axis_names[event.axis]} : {event.value:.2f}")
            elif event.type == pygame.JOYHATMOTION:
                print(f"方向键 : {event.value}")
            else:
                pass
except KeyboardInterrupt:
    print("\n退出")
finally:
    pygame.quit()


