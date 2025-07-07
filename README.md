# DeskRobot 桌面机器人

DeskRobot 是一个树莓派4B驱动的桌面智能机器人伴侣

能够语音对话, OLED显示表情, 人脸跟踪, 网页控制, 手柄控制。

效果展示: https://www.bilibili.com/video/BV1W73AzZEsj/


## 项目结构

- DeskRobot.py ------- 项目入口
- modules ------------- 各个子模块
- configs -------------- 配置文件
- localfiles ------------- 本地资源文件
- requirements.txt ----- 项目依赖
- README.md --------- 说明文档


## 运行

一. VSCode 连接树莓派, 安装 python 插件, 配置 venv 虚拟环境;

克隆代码到树莓派, 打开项目文件夹, 打开 DeskRobot.py, 点击右上角运行;

    本项目高度模块化;

    初始时所有模块已关闭, 没有多余的功能, 也不依赖任何第三方库, 可直接运行;

二. 加载各个模块

编辑 DeskRobot.py 底部区域; 选中相关代码块, 使用 "CTRL+/" 快捷键取消注释以启用;
    
    模块附近的文档已标明该模块的依赖, 按说明安装即可;
    
    如需一次安装所有依赖, 可以执行:
        pip install -r requirements.txt
        注意: requirements.txt 里标注 [手动执行] 的地方是系统依赖, 需手动安装。
        
    一次性安装会比较耗时, 需耐心等待。建议使用国内源加速:
	    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/


三. 配置 API_KEY

    部分模块依赖于第三方在线服务, 运行时需要 API_KEY;
    
	修改 api_config.py, 按指示获取并填写自己 API_KEY;

	目前用我提供的 API_KEY 可以正常运行, 无需修改;
    

## 模块结构

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


## 材料清单

学校提供:

- 树莓派4B
- 舵机云台模块
- DHT11温湿度模块
- RGB三色灯模块

自费购买:
商品名 | 实付 | 购买链接 | 店家
:---   | :--- | :---     | :---
0.96寸OLED显示屏 | ¥5.81| https://detail.tmall.com/item.htm?id=42044259331 | telesky旗舰店
TB6612FNG电机驱动 | ¥5.95 | https://item.taobao.com/item.htm?id=810403532014 | 树莓派零售商
录音麦克风小话筒 | ¥7.65 | https://item.taobao.com/item.htm?id=627272507876 | 树莓派零售商
USB线控迷你小音箱 | ¥11.42 | https://item.taobao.com/item.htm?id=640443690438 | 树莓派零售商
2WD小车底盘(3层) | ¥18.70 | https://item.taobao.com/item.htm?id=696323635690 | 树莓派零售商
160°鱼眼摄像头 | ¥28.65 | https://item.taobao.com/item.htm?id=603972074124 | 树莓派零售商
5V移动电源模块 | ¥26.20 | https://detail.tmall.com/item.htm?id=755340651925 | 辰克旗舰店
合计 | ¥104.38



## 引脚连接


连接            | 内侧引脚 | 外侧引脚 | 连接
---:            | ---:     | :---     | :---
OLED VCC        | 3.3V     | 5V       | TB6612FNG VCC
OLED SDA        | GPIO 2   | 5V       | 俯仰舵机 VCC
OLED SCL        | GPIO 3   | GND      | 
空闲            | GPIO 4   | GPIO 14  | TB6612FNG BIN2
OLED GND        | GND      | GPIO 15  | TB6612FNG BIN1
俯仰舵机 PWM    | GPIO 17  | GPIO 18  | TB6612FNG PWMB
空闲            | GPIO 27  | GND      | 
空闲            | GPIO 22  | GPIO 23  | TB6612FNG AIN2
DHT11 VCC       | 3.3V     | GPIO 24  | TB6612FNG AIN1
LED_R           | GPIO 10  | GND      | DHT11 GND
LED_G           | GPIO 9   | GPIO 25  | DHT11 DATA
LED_B           | GPIO 11  | GPIO 8   | 空闲
LED_GND         | GND      | GPIO 7   | 空闲
空闲            | GPIO 0   | GPIO 1   | 空闲
空闲            | GPIO 5   | GND      | 俯仰舵机 GND
空闲            | GPIO 6   | GPIO 12  | 空闲
空闲            | GPIO 13  | GND      | TB6612FNG GND
TB6612FNG PWMA  | GPIO 19  | GPIO 16  | 空闲
空闲            | GPIO 26  | GPIO 20  | 空闲
空闲            | GND      | GPIO 21  | TB6612FNG STBY


树莓派执行 pinout 命令查看引脚排列; 或者访问 https://pinout.xyz/ 查看详细信息;