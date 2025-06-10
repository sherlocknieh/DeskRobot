"""
共享数据模块
使用单例模式，保证共享数据只存在一个实例
用法:
from modules.SharedData import SharedData
shared_data = SharedData.getinstance()
"""

_instance = None

class SharedData:
    """共享数据类"""
    def __init__(self):
        global _instance
        if _instance is not None:
            raise Exception("This class is a singleton!")
        else:
            _instance = self
        self.data = {}
    
    def getinstance():
        """获取实例"""
        return _instance

    def set_data(self, key, value):
        """设置数据"""
        self.data[key] = value

    def get_data(self, key):
        """获取数据"""
        return self.data.get(key)

