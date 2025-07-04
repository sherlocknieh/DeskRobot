"""配置文件"""


config = {}


# STT 服务商, 可选 'iflytek' 或 'siliconflow'
config["stt_provider"] = 'iflytek'


# 讯飞语音api, 在讯飞开放平台 (https://www.xfyun.cn/) 获取
config["iflytek_app_id"] = "c1eca680"
config["iflytek_api_key"] = "5dfe59ca36641de7dadc0948d7240f2b"
config["iflytek_api_secret"] = "MTZlMjExMGMxN2M4MTgyMjg3Y2E3MTlk"


# Siliconflow 语音合成 API, 在 Siliconflow 开放平台 (https://www.siliconflow.cn/) 获取
config["llm_model_name"] = "Qwen/Qwen3-32B"
config["siliconflow_base_url"] = "https://api.siliconflow.cn/v1"
config["siliconflow_api_key"] = "sk-xgpbdlulapwpsfnzbwoudyzarrzietkkujcajphkvewveykq"

