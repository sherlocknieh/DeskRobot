# DeskRobot 桌面机器人

DeskRobot 是一个树莓派驱动的桌面智能机器人伴侣

能够语音对话, 语音控制, OLED显示表情, 自动人脸跟踪

## 运行

1. 项目使用 Python 3.11 开发，请确保系统中已安装 Python 3.11+;

2. 用 VSCode 打开项目, 打开 DeskRobot.py, 点击右上角运行按钮运行;

    - 本项目高度模块化;
    - 初始时所有模块已关闭, 没有任何功能;
    - 此时不依赖任何第三方库, 可直接运行;

3. 启用模块:

    - 编辑 DeskRobot.py 底部区域;
    - 使用 "CTRL+/" 快捷键取消注释以启用模块;
    - 不同的模块依赖于不同的第三方库;
    - 可按照模块附近的说明文档按需安装;

4. 配置 API_KEY

    - 有的模块依赖于第三方服务, 需要配置 API_KEY;
    - 修改 config.py, 按指示获取并填写 API_KEY;
    - (目前可以不修改, 直接使用我提供的 API_KEY)


## 项目结构

- DeskRobot.py 项目入口。
- modules 存放各个模块。
- configs 存放配置文件。
- localfiles 存放本地资源文件。
- requirements.txt 项目依赖。
    - pip install -r requirements.txt 一键安装。
    - 有些系统依赖无法一键安装, 需按照各模块的说明手动安装。

### 关键模块

- EventBus：使用 "事件总线" 实现各模块间的通信。
- 运动控制模块：使用 gpiozero 控制机器人电机。
- 语音交互模块：
    - 语音唤醒: 使用 openwakeword 实现语音唤醒。
    - 话语检测: 使用 SileroVAD 实现语音监听。
    - STT: 使用 siliconflow_stt 和 iflytek_stt 实现语音转文字。
    - TTS: 使用 edge-tts 实现文字转语音。
- AI对话模块：使用 langchain_openai 和 SiliconFlow API 实现机器人对话。
- OLED显示模块：可显示表情, 文字, 简单动画。
- 人脸跟踪模块：使用 mediapipe 检测人脸, 使用 simple_pid 控制小车跟踪人脸。

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
