"""
终端命令模块
从终端接收特定格式的命令
解析为事件，发布到事件总线
便于对各个模块进行手动调试
"""

import logging
import queue
import threading

from modules.API_EventBus import event_bus
from modules.API_EventBus.event_bus import EventBus

logger = logging.getLogger(__name__)


class IOThread(threading.Thread):
    def __init__(self, event_bus: EventBus):
        super().__init__(daemon=True, name="IOThread")
        self.event_bus = event_bus
        self.event_queue = queue.Queue()
        self._stop_event = threading.Event()
        self.event_bus.subscribe("STOP_THREADS", self.event_queue)

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
                    event_bus.publish("EXIT")
                    break
                if len(input_list)>1:
                    event_payload = input_list[1:]
                    self.event_bus.publish(event_type, source="TERMINAL", **dict(item.split(":") for item in event_payload))
                else:
                    print(f"命令用法: 事件类型 [参数1:值1] [参数2:值2]...")
                    continue
            except EOFError:
                # 当输入流关闭时（例如在某些IDE或管道中），优雅地退出
                break
            except Exception as e:
                logger.error(f"终端输入线程出错: {e}", exc_info=True)
                break

    def stop(self, **kwargs):
        """请求线程停止。"""
        logger.info(f"正在请求停止 {self.name}...")
        self._stop_event.set()


