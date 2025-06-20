import evdev


"""连接手柄"""
def connect_gamepad():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "xbox" in device.name.lower():
            print("Gamepad connected:", device.name)
            return device
    return None

gamepad = connect_gamepad()


"""手柄测试"""
def gamepad_test(gamepad):
    if gamepad is None:
        print("No gamepad found.")
        return
    print("Gamepad found:", gamepad.name)
    for event in gamepad.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            print(f'摇杆事件: {event.code}; 值: {event.value}')
        elif event.type == evdev.ecodes.EV_KEY:
            print(f'按键事件: {event.code}; 值: {event.value}')

"""去抖动的测试"""
def gamepad_test_debounced(gamepad):
    if gamepad is None:
        print("No gamepad found.")
        return
    THRESHOLD = 1
    last_abs_values = 0
    for event in gamepad.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            if abs(event.value - last_abs_values) > THRESHOLD:
                print(f'摇杆事件: {event.code}; 值: {event.value}')
                last_abs_values = event.value
        elif event.type == evdev.ecodes.EV_KEY:
            print(f'按键事件: {event.code}; 值: {event.value}')


gamepad_test_debounced(gamepad)

"""测试结果
    左摇杆:横轴：Code: 0, Value: 0~65535 (左~右)
    左摇杆:纵轴：Code: 1, Value: 0~65535 (上~下)

    右摇杆:横轴：Code: 2, Value: 0~65535 (左~右)
    右摇杆:纵轴：Code: 5, Value: 0~65535 (上~下)

    方向键:左右：Code: 16, Value:-1 (左), 0(放开), 1 (右)
    方向键:上下：Code: 17, Value:-1 (上), 0(放开), 1 (下)

    按键:A：Code: 304, Value: 1 (按下), 0 (放开)
    按键:B：Code: 305, Value: 1 (按下), 0 (放开)
"""


           




