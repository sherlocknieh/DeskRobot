"""
消息总线模块, 各模块的通信中心

使用方法:

# 导入
    from modules.EventBus import EventBus
    event_bus = EventBus()                      # 在任何地方创建 EventBus 对象, 获得的都是同一个实例

# 订阅
    my_queue = queue.Queue()                             # 创建一个自己的事件队列(收件箱)
    event_bus.subscribe("事件类型", my_queue, "订阅人")   # 订阅某种类型的事件 ("订阅人"可不填, 默认为 "")

# 发布
    payload = {"key1": value1, "key2": value2, ...}         # 准备要发布的消息
    event_bus.publish("事件类型", payload, "发布人")         # 发布事件 ("发布人"可不填, 默认为 "UNKNOWN")
    
    # 发送一个事件给总线, 总线就会根据事件类型, 自动将事件转发到订阅者的队列中


# 收取消息
    event = self.my_queue.get()             # 获取一条事件: 如果队列为空, 一直阻塞等待, 直到有事件到来
    event = self.my_queue.getnowait()       # 获取一条事件: 如果队列为空, 返回 None, 并抛出异常(queue.Empty)
    event = self.my_queue.get(timeout=x)    # 获取一条事件: 如果队列为空, 阻塞等待 x 秒, 超时则返回 None, 并抛出异常(queue.Empty)

# 提取消息内容
    event_type = event['type']              # 提取事件的类型: "TYPE1"
    event_data = event['data']              # 提取事件的内容: {"key1": value1, "key2": value2,...}
"""


import threading
import queue
import logging
logger = logging.getLogger(__name__)


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
        # 创建一个空字典, 用于存放订阅队列
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
            raise TypeError(f'{name} 模块使用 subscribe() 时传入了错误的事件容器类型')

        # 事件类型转换为大写字符串
        event_type = str(event_type).upper()

        # 订阅者的队列列表不存在, 则创建
        if event_type not in self.listeners:
            self.listeners[event_type] = []

        # 订阅者的队列列表中不存在该队列, 则添加
        if event_queue not in self.listeners[event_type]:
            self.listeners[event_type].append(event_queue)

        # 打印日志
        logger.info(f'{name} 订阅了 {event_type} 事件')

    def publish(self, event_type, data = {}, source = "未知"):
        # 事件类型转换为大写字符串
        event_type = str(event_type).upper()

        # 如果数据是字符串, 作为 source 处理
        if isinstance(data, str):
            source = data
            data = {}
  
        # 打印日志
        if event_type != "UPDATE_LAYER":            # OLED屏幕刷新事件太频繁，跳过
            logger.info(f'{source} 发布了 {event_type} 事件')
            if data:
                logger.info(f'事件内容: {data}')

        # 丢弃无效的事件类型
        if event_type not in self.listeners:
            if event_type != "UPDATE_LAYER":            # OLED屏幕刷新事件太频繁，跳过
                logger.info(f'{event_type} 事件无人订阅, 已丢弃')
            return
        
        # 将事件类型,数据,发布人打包进字典
        event = {"type": event_type, "data": data, "source": source}

        # 发送给所有订阅者
        for event_queue in self.listeners[event_type]:        
            event_queue.put(event)

