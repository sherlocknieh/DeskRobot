"""终端命令IO模块

接收终端命令，解析参数，发布事件
用于调试其它模块

命令格式: 事件类型 [参数=值] [参数:值] ...

    例如: led_on r=0 g=1 b=0.5
    例如: led_off
    例如: exit
"""


import threading
import logging


from .EventBus import EventBus


class IOThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.name = "终端IO"
        self.event_bus = EventBus()
        self.thread_flag = threading.Event()
        self.logger = logging.getLogger(self.name)


    def run(self):
        self.thread_flag.set()
        self.logger.info("终端IO已启动, 输入指令以发布事件")
        print("格式: 事件类型 [参数=值] [参数:值] ...")
        print("例如: led_on r=0 g=1 b=0.5")
        print("例如: led_off")
        print("例如: exit")
        while self.thread_flag.is_set():
            # 接收命令
            cmd = input('> ').strip().split()
            if not cmd:
                continue
            # 解析命令
            event_type = cmd[0].replace('-', '_')
            if event_type.lower() == 'exit':
                self.event_bus.publish("exit", "终端IO模块")
                self.stop()
                break
            # 解析参数
            data = {}
            for arg in cmd[1:]:
                if '=' in arg:
                    key, value = arg.split('=')
                elif ':' in arg:
                    key, value = arg.split(':')
                try:
                    value = float(value)
                except ValueError:
                    value = str(value)
                data[key.strip()] = value
            self.event_bus.publish(event_type, data, "终端IO模块")

    def stop(self):
        self.logger.info("终端IO模块已退出")
        self.thread_flag.clear()
