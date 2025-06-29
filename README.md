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
修改 configs 中的配置参数
```

4.运行
```bash
python DeskRobot.py
```

## 项目架构

DeskRobot.py 项目入口。

### 主要模块

- 主控模块：使用 EventBus 实现机器人状态控制。
- 运动控制模块：使用 gpiozero 实现机器人电机控制。
- 语音交互模块：
    - 语音唤醒: 使用 openwakeword 实现语音唤醒。
    - 话语检测: 使用 SileroVAD 实现语音断句。
    - STT: 使用 siliconflow_stt 和 iflytek_stt 实现语音转文字。
    - TTS: 使用 edge-tts 实现文字转语音。
- AI对话模块：使用 langchain_openai 和 SiliconFlow API 实现机器人对话。
- OLED显示模块：输入系统状态, 输出表情/内容。
- 人脸跟踪模块：使用 opencv 内置 CascadeClassifier + simple_pid 实现人脸跟踪。

