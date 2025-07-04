# DeskRobot 桌面机器人

DeskRobot 是一个树莓派驱动的桌面智能机器人伴侣

能够语音对话, 语音控制, OLED显示表情, 自动人脸跟踪

## 运行

1. 项目基于 Python 3.11 开发，请确保系统环境中已安装 Python 3.11+;

2. 用 VSCode 打开项目, 打开 DeskRobot.py, 点击右上角运行按钮运行;
```
本项目高度模块化;

初始时所有模块都处于关闭状态, 此时不依赖任何第三方库, 可直接运行;

编辑 DeskRobot.py 底部 if __name__ == "__main__" 区域,

选中对应模块的代码, 使用 "CTRL+/" 快捷键快速取消注释, 即可开启对应模块; 
```


3. 安装依赖
```
pip install -r requirements.txt
```

3.配置 api_key
```
修改 config.py , 填写自己的 api_key
(目前可以不修改, 直接使用我提供的 api_key)
```

4.运行



python DeskRobot.py
```

## 项目架构

DeskRobot.py 项目入口。


### 主要模块

- 主控模块：使用 EventBus 实现机器人状态控制。
- 运动控制模块：使用 gpiozero 实现机器人电机控制。
- 语音交互模块：
    - 语音唤醒| 使用 openwakeword 实现语音唤醒。
    - 话语检测| 使用 SileroVAD 实现语音断句。
    - STT| 使用 siliconflow_stt 和 iflytek_stt 实现语音转文字。
    - TTS| 使用 edge-tts 实现文字转语音。
- AI对话模块：使用 langchain_openai 和 SiliconFlow API 实现机器人对话。
- OLED显示模块：输入系统状态, 输出表情/内容。
- 人脸跟踪模块：使用 opencv 内置 CascadeClassifier + simple_pid 实现人脸跟踪。

## 引脚使用情况
|  引脚 | 连接 |
| ----- | --- |
VCC 3.3V| OLED VCC
VCC 3.3V| DHT11 VCC
VCC 5V  | 舵机 VCC
VCC 5V  | TB6612FNG VCC
GPIO 0  | 空闲
GPIO 1  | 空闲
GPIO 2  | OLED_I2C_SDA
GPIO 3  | OLED_I2C_SCL
GPIO 4  | 空闲
GPIO 5  | 空闲
GPIO 6  | 空闲
GPIO 7  | 空闲
GPIO 8  | 空闲
GPIO 9  | LED_R
GPIO 10 | LED_G
GPIO 11 | LED_B
GPIO 12 | 空闲
GPIO 13 | 空闲
GPIO 14 | TB6612FNG AIN1
GPIO 15 | TB6612FNG AIN2
GPIO 16 | 空闲
GPIO 17 | 舵机 PWM
GPIO 18 | TB6612FNG PWMA
GPIO 19 | TB6612FNG PWMB
GPIO 20 | 空闲
GPIO 21 | TB6612FNG STBY
GPIO 22 | 空闲
GPIO 23 | TB6612FNG BIN1
GPIO 24 | TB6612FNG BIN2
GPIO 25 | DHT11 温湿度传感器
GPIO 26 | 空闲
GPIO 27 | 空闲
