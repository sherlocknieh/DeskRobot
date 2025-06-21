from .event_bus import EventBus

# 导出 EventBus 类, 而非实例。
# 使用单例模式, 各模块通过调用 EventBus() 来获取全局唯一的实例。
# e.g.:
# from modules.EventBus import EventBus
# event_bus = EventBus()

__all__ = ["EventBus"]
