from flask import Flask

app = Flask(__name__)

from .camera import *  # 导入camera模块中的内容

# 其他初始化代码可以放在这里，例如配置设置等