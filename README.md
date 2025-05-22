# DeskRobot

## 构建

1. 安装 [uv](https://github.com/astral-sh/uv)
2. 安装依赖
```bash
# 克隆项目
git clone <repo>
# 进入repo目录
cd <repo>
# 同步uv环境
uv sync --dev
```
3. 在项目目录创建.env文件，示例如下：
```.env
BASE_URL=https://api.deepseek.com
MODEL=deepseek-chat      
OPENAI_API_KEY="sk-xxx"
```
## 运行
```bash
uv run python scripts/main.py
# or
source .venv/bin/activate
python scripts/main.py
```

## 项目架构

DeskRobot 是一个桌面机器人项目，使用模块化架构设计：

### 主要模块

- **agent**: 智能代理模块，负责自然语言处理和与用户交互。
- **control**: 控制模块，包括RoboEyes控制器等。
- **device**: 硬件设备模块，管理OLED显示等物理设备。
- **voice**: 语音处理模块，提供语音合成(TTS)和语音识别(STT)功能。
- **util**: 通用工具和配置模块。

### 单例模式

项目中的关键组件采用单例模式设计，确保全局只有一个实例存在，优化资源利用并简化组件间的协调。

#### 重要的单例类

- **`Agent`**: 智能代理单例，用于处理自然语言交互。
- **`RoboEyesController`**: 控制机器人眼睛动画的单例。
- **`OLEDDisplay`**: OLED显示设备的单例接口。
- **`FastWhisperSTT`**: 语音识别(STT)单例。
- **`PiperTTS`**: 文本转语音(TTS)单例。
- **`VoskSTT`**: 备用语音识别单例。

#### 单例使用指南

获取单例实例请使用各自类的 `get_instance()` 静态方法，而不是直接实例化：

```python
# 正确方式
agent = Agent.get_instance()
oled = OLEDDisplay.get_instance()
tts = PiperTTS.get_instance()

# 错误方式 - 不要这样做
# agent = Agent()  # 这会引发RuntimeError异常！
```

这种方式确保了组件在整个应用程序中的唯一性和一致性。

## tmp

- wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz
- piper tts
- env example

