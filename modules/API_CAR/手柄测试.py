import evdev

摇杆精度 = 65535
扳机精度 = 1023

"""手柄连接程序"""
def connect_gamepad():
    global 摇杆精度, 扳机精度
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        print(device.name)

    for device in devices:
        if "XBOX" in device.name.upper():
            print("Gamepad connected:", device.name)
            摇杆精度 = 65535
            扳机精度 = 1023
            return device
        elif device.name =="GameSir-Nova Lite":
            print("Gamepad connected:", device.name)
            摇杆精度 = 255
            扳机精度 = 255
            return device
    return None


""" 手柄测试 """
def gamepad_test():
    gamepad = connect_gamepad()
    if gamepad is None:
        print("No gamepad found.")
        return
    for event in gamepad.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            print(f'摇杆事件: {event.code}; 值: {event.value}')
        elif event.type == evdev.ecodes.EV_KEY:
            print(f'按键事件: {event.code}; 值: {event.value}')


""" 手柄按键测试 """
def gamepad_test2():
    gamepad = connect_gamepad()
    if gamepad is None:
        print("No gamepad found.")
        return
    x = 0
    y = 0
    z = 0
    for event in gamepad.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            print(f'摇杆事件: {event.code}; 值: {event.value}')
            if event.code == 0:
                x = event.value/摇杆精度*2-1
            elif event.code == 1:
                y = -event.value/摇杆精度*2+1
            elif event.code == 16:
                x = event.value
            elif event.code == 17:
                y = -event.value
            # 右扳机
            elif event.code == 9:
                z = -event.value/扳机精度
            # 左扳机
            elif event.code == 10:
                z = event.value/扳机精度
            print(f'x: {x:.2f}, y: {y:.2f}, z: {z:.2f}')
        elif event.type == evdev.ecodes.EV_KEY:
            print(f'按键事件: {event.code}; 值: {event.value}')

"""启动测试"""
gamepad_test2()




