# DeskRobot 桌面机器人

DeskRobot 是一个树莓派4B驱动的桌面智能机器人伴侣

能够语音对话, 语音控制, OLED显示表情, 自动人脸跟踪


## 项目结构

- DeskRobot.py ------- 项目入口
- modules ------------- 各个子模块
- configs -------------- 配置文件
- localfiles ------------- 本地资源文件
- requirements.txt ----- 项目依赖
- README.md --------- 说明文档


## 运行

1. VSCode 连接树莓派, 安装 python 插件, 配置 venv 虚拟环境;

    克隆代码到树莓派, 打开项目文件夹, 打开 DeskRobot.py 点击右上角运行;

    - 本项目高度模块化;
    - 初始时所有模块已关闭, 没有任何功能;
    - 此时不依赖任何第三方库, 可直接运行;

2. 加载各个模块

    - 编辑 DeskRobot.py 底部区域;
    - 使用 "CTRL+/" 快捷键取消注释相关代码以启用模块;
    - 模块附近的文档会标明模块的依赖, 按说明安装即可;
    
    如需一次性安装所有依赖, 可以执行 pip install -r requirements.txt 命令。
    
    注意 requirements.txt 里标注了 [手动执行] 的地方是系统依赖, 需手动安装。
    
    会比较耗时, 请耐心等待。


3. 配置 API_KEY

    - 部分模块依赖于第三方在线服务, 运行前需要配置 API_KEY;
    - 目前可以不修改, 用我提供的 API_KEY 可以正常运行;
    - 也可以修改 api_config.py, 按指示获取并填写自己 API_KEY;



### 关键模块

- EventBus：使用 "事件总线" 实现各模块间的通信。
- 运动控制模块：使用 gpiozero 控制机器人电机。
- 语音交互模块：
    - 语音唤醒: 使用 openwakeword 实现语音唤醒。
    - 话语检测: 使用 SileroVAD 实现语音监听。
    - STT: 使用 siliconflow_stt 和 iflytek_stt 实现语音转文字。
    - TTS: 使用 edge-tts 实现文字转语音。
- AI对话模块：使用 langchain_openai 和 SiliconFlow API 实现机器人对话。
- OLED显示模块：使用 luma.oled + Roboeyes 库实现表情显示, 手写了文字显示。
- 人脸跟踪模块：使用 mediapipe 检测人脸, 使用 simple_pid 控制小车跟踪人脸。

## 引脚连接情况 (按树莓派4B引脚排列)

|  内侧 | 连接 |
| ----- | --- |
VCC 3.3V| OLED VCC
GPIO 2  | OLED SDA
GPIO 3  | OLED SCL
GPIO 4  | 空闲
GND     | OLED GND
GPIO 17 | 俯仰舵机 PWM
GPIO 27 | 空闲
GPIO 22 | 空闲
VCC 3.3V| DHT11 VCC
GPIO 10 | LED_R
GPIO 9  | LED_G
GPIO 11 | LED_B
GND     | LED_GND
GPIO 0  | 空闲
GPIO 5  | 空闲
GPIO 6  | 空闲
GPIO 13 | 空闲
GPIO 19 | TB6612FNG PWMA
GPIO 26 | 空闲


|  外侧 | 连接 |
| ----- | --- |
VCC 5V  | TB6612FNG VCC
VCC 5V  | 俯仰舵机 VCC
GND     | GND
GPIO 14 | TB6612FNG BIN2
GPIO 15 | TB6612FNG BIN1
GPIO 18 | TB6612FNG PWMB
GND     | GND
GPIO 23 | TB6612FNG AIN2
GPIO 24 | TB6612FNG AIN1
GND     | DHT11 GND
GPIO 25 | DHT11 DATA
GPIO 8  | 空闲
GPIO 7  | 空闲
GPIO 1  | 空闲
GND     | 俯仰舵机 GND
GPIO 12 | 空闲
GND     | TB6612FNG GND
GPIO 16 | 空闲
GPIO 20 | 空闲
GPIO 21 | TB6612FNG STBY