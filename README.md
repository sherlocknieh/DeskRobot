# DeskRobot

## 构建

1. 安装 [uv](https://github.com/astral-sh/uv)
2. 在项目目录创建.env文件，示例如下：
```.env
BASE_URL=https://api.deepseek.com
MODEL=deepseek-chat      
OPENAI_API_KEY="sk-xxx"
```
3. 安装依赖
```bash
# 克隆项目
git clone <repo>
# 进入repo目录
cd <repo>
# 同步uv环境
uv sync --dev


```
## 运行
```bash
uv run python scripts/main.py
# or
source .venv/bin/activate
python scripts/main.py
```