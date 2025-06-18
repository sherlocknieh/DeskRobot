"""
全局事件总线模块 (发布/订阅模式)

提供一个单例的 EventBus 实例，用于在系统各模块之间进行事件驱动的通信。

使用方法:
from modules.event_bus import event_bus

# 发布事件 (新方法)
event_bus.publish("EVENT_NAME", source="module_name", payload1="value1", ...)

# 订阅事件
# 1. 在你的线程 __init__ 中:
self.my_queue = queue.Queue()
event_bus.subscribe("EVENT_NAME", self.my_queue)

# 2. 在你的线程 run() 循环中:
event = self.my_queue.get()
if event['type'] == "EVENT_NAME":
    # process event['payload']
"""

import logging
import queue
from collections import defaultdict
from typing import Any, Dict

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        # 使用 defaultdict 可以让订阅者列表在第一次访问时自动创建为空列表
        self.listeners: Dict[str, list[queue.Queue]] = defaultdict(list)

    def subscribe(self, event_type: str, listener_queue: queue.Queue):
        """
        订阅一个特定类型的事件。
        一个模块线程应该创建自己的Queue，并用它来订阅自己感兴趣的事件。

        Args:
            event_type: 事件类型 (e.g., "DISPLAY_IMAGE")
            listener_queue: 监听者的私有队列，用于接收事件
        """
        if not isinstance(listener_queue, queue.Queue):
            raise TypeError("listener_queue 必须是一个 queue.Queue 实例。")

        self.listeners[event_type].append(listener_queue)
        # 增强日志：记录订阅者的内存地址以区分不同实例
        logger.info(
            f"E-BUS: 订阅事件 => 类型='{event_type}', 订阅者队列='{listener_queue}'"
        )

    def publish(self, event_type: str, **kwargs: Any):
        """
        发布一个事件。 (新版方法)
        事件总线会将此事件分发给所有订阅了该事件类型的监听者。

        Args:
            event_type: 事件的类型 (e.g., "STT_RESULT_CAPTURED")
            **kwargs: 任意数量的关键字参数，将作为事件的 payload。
                      例如: text="你好", source="AiThread"
        """
        # 将事件类型和数据负载组装成标准的事件字典
        event: Dict[str, Any] = {"type": event_type, "payload": kwargs}

        source = kwargs.get("source", "未知来源")
        # 增强日志：记录发布的完整事件内容
        if event_type != "DISPLAY_IMAGE":
            logger.info(
                f"E-BUS: 发布事件 => 类型='{event_type}', 来源='{source}', 内容={kwargs}"
            )

        # 检查是否有订阅者
        if event_type not in self.listeners:
            logger.warning(f"E-BUS: 事件 '{event_type}' 无任何订阅者。")
            return

        # 增强日志：记录事件分发给了哪些订阅者
        if event_type != "DISPLAY_IMAGE":
            logger.info(
                f"E-BUS: 分发事件 '{event_type}' 给 {len(self.listeners[event_type])} 个订阅者:"
            )
        for listener_queue in self.listeners[event_type]:
            logger.debug(f"    -> 队列: {listener_queue}")
            listener_queue.put(event)



def cmd_to_event(event_bus):
    """
    解析命令字符串, 发布对应的事件
    cmd = "led on 1 0 0"
    发布事件: event_type = "LED", payload={"on", "1", "0", "0"}
    """
    cmd = input("请输入命令: ")
    event_type = cmd.split()[0]
    payload = cmd.split()[1:]
    event_bus.publish(event_type, **dict(zip(payload[::2], payload[1::2])))
    