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
3. 根据下面的项目配置，配置项目根目录，模型文件路径等。

## 运行
```bash
uv run python src/DeskRobot/main.py
```

## 项目架构

DeskRobot 是一个在树莓派上运行的语音机器人项目，使用uv管理依赖，使用单例模式设计，使用模块化架构设计。
### 主要模块

- **agent**: 代理模块，负责与用户交互，使用llm处理用户输入，并返回响应，且调用其他模块调整机器人状态。
- **control**: 控制模块，包括RoboEyes控制器等。
- **device**: 硬件设备模块，管理OLED显示等物理设备。
- **voice**: 语音处理模块，提供语音合成(TTS)和语音识别(STT)功能，使用piper和fast-whisper。
- **util**: 通用工具和配置模块，包括配置文件，项目根目录等。

### 单例模式

项目中的关键组件采用单例模式设计，确保全局只有一个实例存在，优化资源利用并简化组件间的协调。

#### 重要的单例类

- **`Agent`**: 代理单例，用于处理自然语言交互。
- **`RoboEyesController`**: 控制机器人眼睛动画的单例，通过OLED单例输出到OLED设备。
- **`OLEDDisplay`**: OLED显示设备的单例接口，用于显示机器人状态。
- **`FastWhisperSTT`**: 语音识别(STT)单例，使用fast-whisper。
- **`PiperTTS`**: 文本转语音(TTS)单例，使用piper。
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

## 项目配置

### `PROJECT_ROOT` 参数

`PROJECT_ROOT` 参数用于指定项目的根目录。

- **配置方式**: 你可以在 `src/DeskRobot/util/config.py` 文件中设置此参数，或者将其设置为操作系统的环境变量。

### 配置文件

配置文件存放在项目根目录下的 `.env` 文件中。

**如何配置**:
1. 复制 `.env.example` 文件为 `.env` 文件。
2. 打开 `.env` 文件，根据你的实际情况填写配置值。

### 模型文件 (`dn` 目录)

本项目依赖的一些模型文件（如 Piper TTS, Vosk STT, Fast Whisper）存放在项目根目录下的 `dn` 文件夹内。

- **如何准备**: 你需要根据 `src/DeskRobot/util/config.py` 文件中定义的相关路径 (例如 `dn/piper/model`, `dn/vosk/model`, `dn/fast-whisper/model`)，自行下载或准备这些模型文件，并将它们放置在对应的 `dn` 子目录中。 

- piper：在[piper](https://github.com/rhasspy/piper/blob/master/VOICES.md)中选择一个模型和对应配置文件，下载到 `dn/piper/model` 文件夹内。
   - 我们使用`zh_CN-huayan-x_low.onnx`模型，下载到 `dn/piper/model` 文件夹内。
   - 下载对应配置文件`zh_CN-huayan-x_low.json`，存放在 `dn/piper/model` 文件夹内。
   - 此外，还需要在[piper的release](https://github.com/rhasspy/piper/releases/)中，下载[piper_linux_aarch64.tar.gz](https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz)，并解压到`dn/piper`文件夹内。

- vosk：在[vosk的模型列表](https://alphacephei.com/vosk/models)中选择一个模型，下载到 `dn/vosk/model` 文件夹内。
   - 我们使用[vosk-model-small-cn-0.22](https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip)模型。

- fast-whisper：fast-whisper运行时发现没有模型文件，会自动下载模型文件，将会下载到src/DeskRobot/util/config.py中定义的`FAST_WHISPER_MODEL_PATH`路径下。

### other目录
other目录下存放了一些文件，包括：

- remote_audio_tester.py: 如果你的树莓派没有麦克风和扬声器，可以使用这个脚本测试麦克风和扬声器是否正常工作，它在你的电脑上运行，将使用你电脑上的麦克风和扬声器。


