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
3. 复制项目根目录下的 `.env.example` 文件为 `.env` (如果 `.env.example` 不存在，请参照下面的示例手动创建)。
   然后根据你的实际环境修改 `.env` 文件中的配置。示例如下：
```.env
BASE_URL=https://api.deepseek.com
MODEL=deepseek-chat      
OPENAI_API_KEY="sk-xxx"
# PROJECT_ROOT=/path/to/your/DeskRobot # 可选，若不设置则自动推断
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

## 项目配置

### `PROJECT_ROOT` 环境变量

`PROJECT_ROOT` 环境变量用于指定项目的根目录。

- **配置方式**: 你可以在 `.env` 文件中设置此变量，或者将其设置为操作系统的环境变量。
- **自动推断**: 如果没有显式设置 `PROJECT_ROOT`，项目会根据 `src/DeskRobot/util/config.py` 文件的位置自动推断出项目的根目录。

### `.env` 和 `.env.example` 文件

- **`.env`**: 此文件用于存储敏感的配置信息和环境变量，例如 API 密钥。**此文件不应提交到 Git 版本控制中。**
- **`.env.example`**: 这是 `.env` 文件的一个模板，列出了项目运行所需的配置项及其格式。它帮助开发者了解需要设置哪些环境变量。

**如何配置**:
1. 将项目根目录下的 `.env.example` 文件复制并重命名为 `.env`。
2. 打开 `.env` 文件，根据你的实际情况填写配置值。

### 模型文件 (`dn` 目录)

本项目依赖的一些大型模型文件（如 Piper TTS, Vosk STT, Fast Whisper）存放在项目根目录下的 `dn` 文件夹内。

- **重要提示**: 这些模型文件由于体积较大，**并未包含在 Git 仓库中**。
- **如何准备**: 你需要根据 `src/DeskRobot/util/config.py` 文件中定义的相关路径 (例如 `dn/piper/model`, `dn/vosk/model`, `dn/fast-whisper/model`)，自行下载或准备这些模型文件，并将它们放置在对应的 `dn` 子目录中。
- **版本控制**: 强烈建议将 `dn/` 目录添加到你的 `.gitignore` 文件中，以避免将这些大型文件意外提交到版本库。 例如，在 `.gitignore` 文件中添加一行：
  ```gitignore
  dn/
  ```

