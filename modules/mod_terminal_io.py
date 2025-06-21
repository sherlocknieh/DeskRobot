"""终端命令模块
从终端接收特定格式的命令，
解析为事件并发布到事件总线，
便于对各个模块进行手动调试。
"""


if __name__ == '__main__':
    from event_bus import EventBus
else:
    from .event_bus import EventBus


import queue
import threading
import re


class IOThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event_bus = EventBus()
        self.event_queue = queue.Queue()
        self.thread_flag = threading.Event()

    def run(self):
        self.thread_flag.set()

        pattern = r'(\w+)\s*(=|:)\s*("[^"]*"|[^\s"\']+|\'[^\']*\')'
        print("格式: 事件类型[:动作] [参数:值] [参数=值] ...")
        print("例如: led:on r=0 g=1 b=0.5")
        print("例如: led:off")
        print("例如: exit")

        while self.thread_flag.is_set():
            try:
                s = input('>').strip()
                if s == "exit":
                    self.event_bus.publish("exit")
                    self.stop()
                    break
                matches = re.findall(pattern, s)
                params = {}
                for key, sep, value in matches:

                    value = value.strip('"\'')  # 去除引号
                    try:
                        value = float(value)    # 尝试转换为浮点数
                    except ValueError:
                        pass                    # 若转换失败，则保持原值
                    params[key] = value         # 存入参数字典
                event_type = s.split()[0].upper()
                if ':' in event_type: 
                    event_type = event_type.split(':')[0].upper()
                self.event_bus.publish(event_type, data=params)  # 发布事件
            except EOFError or KeyboardInterrupt or Exception:
                self.event_bus.publish("exit")
                self.stop()
                break

    def stop(self):
        self.thread_flag.clear()


if __name__ == '__main__':

    """
    测试:
        单独测试时没有订阅者，发送的事件会被丢弃
        完整效果需在主程序中配合其它模块测试
    """
    io_thread = IOThread()

    io_thread.start()

    io_thread.join()
