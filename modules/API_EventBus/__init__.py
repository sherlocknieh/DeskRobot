from .event_bus import EventBus

# 创建一个唯一的、全局的事件总线实例
# 所有模块都应该从这里导入它，以确保是同一个对象
# e.g. from modules import event_bus
event_bus = EventBus.get_instance()
