import evdev


"""手柄连接程序"""
def connect_gamepad():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "xbox" in device.name.lower():
            print("Gamepad connected:", device.name)
            return device
    print("No gamepad found.")
    return None


"""手柄测试程序"""
def gamepad_test():
    gamepad = connect_gamepad()
    if gamepad is None:
        print("No gamepad found.")
        return
    x = 0
    y = 0
    for event in gamepad.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            if event.code == 0:
                x = event.value/65535*2-1
            elif event.code == 1:
                y = -event.value/65535*2+1
            elif event.code == 16:
                x = event.value
            elif event.code == 17:
                y = -event.value
            print(f'x: {x:.2f}, y: {y:.2f}')
        elif event.type == evdev.ecodes.EV_KEY:
            print(f'按键事件: {event.code}; 值: {event.value}')


"""启动测试"""
gamepad_test()




