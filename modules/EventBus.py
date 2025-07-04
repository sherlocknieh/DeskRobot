"""
消息总线模块, 各模块的通信中心

使用方法:

# 导入
    from .EventBus import EventBus
    event_bus = EventBus()                      # 在任何地方创建 EventBus 对象, 获得的都是同一个实例

# 订阅
    my_queue = queue.Queue()                             # 创建一个自己的事件队列(收件箱)
    event_bus.subscribe("类型", my_queue, "订阅人")   # 订阅某种类型的事件 ("订阅人"可不填, 默认为空字符串)

# 发布
    data = {"key1": value1, "key2": value2, ...}         # 以字典格式准备要发布的消息
    event_bus.publish("类型", data, "发布人")         # 发布事件 ("发布人" 和 data 顺序随意, 可不填, 也可只填其中一个)
    
    # 发送一个事件给总线, 总线就会根据事件类型, 自动将事件转发到订阅者的队列中

# 获取消息
    event = self.my_queue.get()             # 获取一条事件: 如果队列为空, 一直阻塞等待, 直到有事件到来
    event = self.my_queue.getnowait()       # 获取一条事件: 如果队列为空, 立即返回 None, 并抛出异常(queue.Empty)
    event = self.my_queue.get(timeout=x)    # 获取一条事件: 如果队列为空, 阻塞等待 x 秒, 超时则返回 None, 并抛出异常(queue.Empty)

# 查看消息
    type   = event['type']              # 提取类型信息
    data   = event['data']              # 提取内容信息
    sender = event['source']            # 提取发布人信息
"""


import threading
import queue
import logging
logger = logging.getLogger("消息总线")


class EventBus:
    _instance = None
    _lock = threading.Lock()
    def __new__(cls):
        """实现单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "listeners"):   # 避免多次初始化
            self.listeners = {}
            """实际结构:
            self.listeners = {
                "TYPE1": [queue1, queue2, queue3],
                "TYPE2": [queue1, queue4],
                "TYPE3": [queue2],
            }
            """

    def subscribe(self, event_type, event_queue, name = ""):
        if not isinstance(event_queue, queue.Queue):
            raise TypeError(f'{name} 模块使用 subscribe() 时传入了错误的容器类型')

        # 事件类型转换为大写字符串
        event_type = str(event_type).upper()

        # 订阅者的队列列表不存在, 则创建
        if event_type not in self.listeners:
            self.listeners[event_type] = []

        # 订阅者的队列列表中不存在该队列, 则添加
        if event_queue not in self.listeners[event_type]:
            self.listeners[event_type].append(event_queue)

        # 打印日志
        logger.info(f'{name} 订阅了 {event_type} 消息')

    def publish(self, event_type, data = {}, source = "未知"):
        # 事件类型转换为大写字符串
        event_type = str(event_type).upper()

        # 如果 data 是字符串, 则与 source 交换数据
        if isinstance(data, str):
            source, data = data, source
            if data == "未知": data = {}

        # 打印日志
        # 对于高频或data过大的事件，在此处列出以禁止其内容被打印到日志。
        frequent_event_types = [
            "UPDATE_LAYER",             # OLED屏幕刷新事件,非常频繁
            "VOICE_COMMAND_DETECTED",   # VAD检测到语音结束,data较大,不打印
            "NEW_FRAME",
            "CAR_STEER",
            "HEAD_ANGLE",
        ]
        # 打印事件发布日志
        if event_type not in frequent_event_types:
            logger.info(f'{source} 发布了 {event_type} 消息')
            if data:
                import json
                print("data = ",json.dumps(data, indent=4,ensure_ascii=False))


        # 丢弃未被订阅的事件, 并打印日志
        if event_type not in self.listeners:
            if event_type not in frequent_event_types:
                logger.info(f'{source} 发布的 {event_type} 消息无人订阅, 已丢弃')
            return
        
        # 将事件类型,数据,发布人打包进字典
        event = {"type": event_type, "data": data, "source": source}

        # 发送给所有订阅者
        for event_queue in self.listeners[event_type]:
            event_queue.put(event)