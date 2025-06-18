"""
各模块的数据交换中心
"""
import threading
import time
import copy
import json


class DataCenter:
    def __init__(self):
        self.LED_status = {
            "status": "off",
            "r" : 1,
            "g" : 1,
            "b" : 1,
            "speed": 1,
        }
