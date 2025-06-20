"""
数据中心模块, 各模块间通信的统一入口

使用方法:
    # 导入和实例化
    from modules.DataCenter import EventBus
    event_bus = EventBus()

    # 订阅事件
    self.my_queue = queue.Queue()                          # 创建一个自己的事件队列(收件箱)
    event_bus.subscribe("TYPE1", self.my_queue, "订阅人")   # 订阅某种类型的事件(订阅人选填)

    # 发布事件
    event_bus.publish("TYPE1", key1=value1, key2=value2, ...)
    
    # 发送一个事件给总线, 事件类型为 "TYPE1", 内容为 {"key1": value1, "key2": value2, ...}
    # 每当有模块发布事件, 总线就会根据事件类型, 将事件转发到订阅者的队列中

    
    # 事件的收取与使用
    event = self.my_queue.get()             # 获取一条事件: 如果队列为空, 一直阻塞等待, 直到有事件到来
    event = self.my_queue.getnowait()       # 获取一条事件: 如果队列为空, 返回 None, 并抛出异常(queue.Empty)
    event = self.my_queue.get(timeout=x)    # 获取一条事件: 如果队列为空, 阻塞等待 x 秒, 超时则返回 None, 并抛出异常(queue.Empty)

    event_type = event['type']              # 提取事件的类型: "TYPE1"
    event_payload = event['payload']        # 提取事件的内容: {"key1": value1, "key2": value2,...}
"""

import queue
import logging
from collections import defaultdict
from typing import Any, Dict

logger = logging.getLogger(__name__)


class EventBus:
    _instance = None

    @staticmethod
    def get_instance():
        if EventBus._instance is None:
            EventBus._instance = EventBus()
        return EventBus._instance

    def __init__(self):
        # 创建一个空字典, 用于存放订阅队列
        self.listeners: Dict[str, list[queue.Queue]] = defaultdict(list)
        """实际结构:
        self.listeners = {
            "TYPE1": [queue1, queue2, queue3],
            "TYPE2": [queue1, queue4],
            "TYPE3": [queue2],
        }
        """

    def subscribe(self, event_type: str, listener_queue: queue.Queue, subscriber_name: str = "未知订阅者"):
        if not isinstance(listener_queue, queue.Queue):
            raise TypeError(f'"{subscriber_name}" 传入了错误的事件容器')

        self.listeners[event_type].append(listener_queue)
        # 增强日志：记录订阅者的内存地址以区分不同实例
        logger.info(
            f'EVENT: "{subscriber_name}" 订阅了 "{event_type}" 事件'
        )

    def publish(self, event_type: str, **kwargs: Any):
        # 将事件类型和数据组装成一个字典
        event: Dict[str, Any] = {"type": event_type, "payload": kwargs}
        
        # 发送给所有订阅者
        for listener_queue in self.listeners[event_type]:
            listener_queue.put(event)

        # 打印事件处理过程
        source = kwargs.get("source", "未知来源")    # 获取事件来源
        if event_type != "UPDATE_LAYER":            # OLED屏幕刷新事件太频繁，跳过
            logger.info(f'EVENT: "{source}" 发布了 "{event_type}" 事件, 内容 = {kwargs}')

        if event_type not in self.listeners:
            logger.warning(f'EVENT: 事件 "{event_type}" 无人订阅, 已丢弃')
            return
