import logging

import requests

# 从环境变量或配置文件中获取API密钥
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"

logger = logging.getLogger("SiliconFlowSTT")


class SiliconFlowSTT:
    def __init__(
        self,
        api_key: str,
        model_name: str = "FunAudioLLM/SenseVoiceSmall",
        language: str = "auto",
    ):
        """
        初始化 SiliconFlow STT 服务。
        :param api_key: SiliconFlow API 密钥。
        :param model_name: 要使用的语音识别模型。
        :param language: 语音的语言代码 (例如 "zh", "en")。'auto' 为自动检测。
        """
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("未提供 SiliconFlow API key。")
        self.model_name = model_name
        self.language = language
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        logger.info(
            f"SiliconFlowSTT 初始化, 模型: {self.model_name}, 语言: {self.language}"
        )

    def speech_to_text(
        self, audio_data: bytes, audio_format: str = "wav"
    ) -> str:
        """
        通过上传内存中的音频数据，使用 SiliconFlow API 将音频转换为文本。
        :param audio_data: 音频数据的字节流。
        :param audio_format: 音频格式, e.g., "wav", "mp3"。
        """
        try:
            data = {"model": self.model_name, "language": self.language}
            files = {
                "file": (
                    f"audio.{audio_format}",
                    audio_data,
                    f"audio/{audio_format}",
                )
            }
            logger.info(f"正在调用 SiliconFlow API (内存数据)...")
            response = requests.post(
                SILICONFLOW_API_URL, headers=self.headers, data=data, files=files
            )
            response.raise_for_status()
            result = response.json()
            recognized_text = result.get("text", "")
            logger.info(f"SiliconFlow API 响应: {recognized_text}")
            return recognized_text
        except requests.exceptions.RequestException as e:
            logger.error(f"调用 SiliconFlow API 时出错: {e}")
            if e.response:
                logger.error(f"响应内容: {e.response.text}")
            return ""
        except Exception as e:
            logger.error(f"处理 SiliconFlow STT 时发生错误: {e}", exc_info=True)
            return ""
