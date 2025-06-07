# DeskRobot 桌面机器人

DeskRobot 是一个桌面智能机器人伴侣

能够语音对话, 语音控制移动, OLED显示信息, 自动跟踪人脸

## 运行

1.安装 Python 3.10+

2.安装依赖
```bash
pip install -r requirements.txt
```

3.配置参数
```
修改 xxx.py 文件中以下参数：
```

4.运行
```bash
python DeskRobot.py
```

## 项目架构

DeskRobot.py 项目入口。

### 主要模块

- 主控模块：使用...实现机器人状态控制。
- 运动控制模块：使用...实现机器人运动控制。
- 语音控制模块：使用...实现语音控制。
- AI对话模块：使用...实现机器人对话。
- OLED显示模块：输入系统状态, 输出表情/内容。
- 人脸跟踪模块：使用...实现人脸跟踪。


## GPIO使用情况

GPIO 0:  空闲
GPIO 1:  空闲
GPIO 2:  OLED_I2C_SDA
GPIO 3:  OLED_I2C_SCL
GPIO 4:  空闲
GPIO 5:  空闲
GPIO 6:  空闲
GPIO 7:  空闲
GPIO 8:  空闲
GPIO 9:  空闲
GPIO 10: 空闲
GPIO 11: 空闲
GPIO 12: 空闲
GPIO 13: 空闲
GPIO 14: Car Motor 1
GPIO 15: Car Motor 1
GPIO 16: 空闲
GPIO 17: 空闲
GPIO 18: Car PWM 1
GPIO 19: Car PWM 2
GPIO 20: 空闲
GPIO 21: 空闲
GPIO 22: 空闲
GPIO 23: Car Motor 2
GPIO 24: Car Motor 2
GPIO 25: 空闲
GPIO 26: 空闲
GPIO 27: 空闲

