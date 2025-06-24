"""终端命令IO模块

接收终端命令，解析参数，发布事件
用于调试其它模块

命令格式: 事件类型 [参数=值] [参数:值] ...

    例如: led_on r=0 g=1 b=0.5
    例如: led_off
    例如: exit
"""


if __name__ == '__main__':
    from EventBus import EventBus   # 直接运行时使用, 用于测试
else:
    from .EventBus import EventBus  # 被上级模块导入时使用


import threading


class IOThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event_bus = EventBus()
        self.thread_flag = threading.Event()

    def run(self):
        self.thread_flag.set()
        print("IO线程已启动")
        print("命令格式: 事件类型 [参数=值] [参数:值] ...")
        print("例如: led_on r=0 g=1 b=0.5")
        print("例如: led_off")
        print("例如: exit")
        while self.thread_flag.is_set():
            cmd = input('> ').strip().split()
            if not cmd:
                continue
            # 解析命令
            event_type = cmd[0].replace('-', '_')
            if event_type.lower() == 'exit':
                self.event_bus.publish("exit", {}, "IO线程")
                self.stop()
                break
            # 解析参数
            payload = {}
            for arg in cmd[1:]:
                if '=' in arg:
                    key, value = arg.split('=')
                elif ':' in arg:
                    key, value = arg.split(':')
                try:
                    value = float(value)
                except ValueError:
                    value = str(value)
                payload[key.strip()] = value
            self.event_bus.publish(event_type, payload, "IO线程")

    def stop(self):
        print("IO线程已退出")
        self.thread_flag.clear()


if __name__ == '__main__':

    """ 测试: """

    # 设置日志格式
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s][%(levelname)s]%(message)s",
    )
    # 启动IO线程
    IOThread().start()
