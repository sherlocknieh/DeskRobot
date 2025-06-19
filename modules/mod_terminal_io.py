"""
终端命令模块
从终端接收特定格式的命令
解析为事件，发布到事件总线
便于对各个模块进行手动调试
"""

import logging
import queue
import threading

logger = logging.getLogger(__name__)


class IOThread(threading.Thread):
    def __init__(self, event_bus):
        super().__init__(daemon=True, name="IOThread")
        self.event_bus = event_bus
        self.event_queue = queue.Queue()
        self._stop_event = threading.Event()

    def run(self):
        self.event_bus.publish("THREAD_STARTED", name=self.__class__.__name__)
        
        print(f"命令用法: 事件类型 [参数1:值1] [参数2:值2]...")
        print('例如: "LED action:on r:0 g:1 b:0.5"')
        print('例如: "LED action:off"')
        print("输入 'exit' 或 'quit' 或 'stop' 退出程序")
        while True:
            try:
                text = input('Input: ').strip()
                if not text: continue
                if text.startswith("#"): continue
                input_list = text.split()
                event_type = input_list[0]
                if event_type in ["exit", "quit", "stop"]:
                    self.event_bus.publish("EXIT")
                    break
                event_payload = {}
                if len(input_list)>1:
                    event_payload = input_list[1:]
                    event_payload = dict(item.split(":") for item in event_payload)
                self.event_bus.publish(event_type, source="TERMINAL", **event_payload)
            except EOFError:
                # 当输入流关闭时（例如在某些IDE或管道中），优雅地退出
                break
            except Exception as e:
                print(f"终端输入线程出错: {e}")
                break

    def stop(self, **kwargs):
        """请求线程停止。"""
        print(f"正在停止 {self.name}")
        self._stop_event.set()


if __name__ == '__main__':

    from API_EventBus import event_bus
    io_thread = IOThread(event_bus)
    io_thread.start()
    io_thread.join()