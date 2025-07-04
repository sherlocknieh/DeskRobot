import logging
import os
import tempfile
import threading
import wave
from queue import Empty, Queue

from .API_Voice.STT.iflytek_stt import IflytekSTTClient
from .API_Voice.STT.siliconflow_stt import SiliconFlowSTT
from .EventBus import EventBus

logger = logging.getLogger("STT模块")


class STTThread(threading.Thread):
    """
    语音转文本（STT）处理线程。

    该线程负责将录制的音频数据转换为文本。

    subscribe:
    - VOICE_COMMAND_DETECTED: 接收到完整的语音指令时触发。
        - data: {"audio_data": bytes, "sample_rate": int, "channels": int}
    - EXIT: 停止线程。

    publish:
    - STT_RESULT_RECEIVED: 成功识别出文本后发布。
        - data: {"text": str}
    - ERROR: 发生错误时发布。
        - data: {"message": str}
    """

    def __init__(self, config: dict):
        super().__init__()
        self.daemon = True
        self.name = "STT Thread"
        self.event_bus = EventBus()
        self.config = config
        self.event_queue = Queue()
        self.stop_event = threading.Event()
        self.stt_client = None
        logger.info("STTThread 初始化完成。")

    def _setup(self):
        """根据配置初始化 STT 客户端。"""
        stt_provider = self.config.get("stt_provider", "siliconflow").lower()
        logger.info(f"正在设置 STT 提供商: {stt_provider}")

        try:
            if stt_provider == "iflytek":
                app_id = self.config.get("iflytek_app_id")
                api_key = self.config.get("iflytek_api_key")
                api_secret = self.config.get("iflytek_api_secret")
                if not all([app_id, api_key, api_secret]):
                    logger.error("讯飞 STT 配置不完整 (APPID, APIKey, APISecret)。")
                    return False
                self.stt_client = IflytekSTTClient(
                    appid=app_id, apikey=api_key, apisecret=api_secret
                )
                logger.info("讯飞 STT 客户端创建成功。")

            elif stt_provider == "siliconflow":
                api_key = self.config.get("siliconflow_api_key")
                if not api_key:
                    logger.error("SiliconFlow STT API Key 未提供。")
                    return False
                self.stt_client = SiliconFlowSTT(api_key=api_key, language="zh")
                logger.info("SiliconFlow STT 客户端创建成功。")

            else:
                logger.error(f"不支持的 STT 提供商: {stt_provider}")
                return False

            self.event_bus.subscribe(
                "VOICE_COMMAND_DETECTED", self.event_queue, self.name
            )
            self.event_bus.subscribe("EXIT", self.event_queue, self.name)
            logger.info("STTThread 底层组件设置成功。")
            return True

        except Exception as e:
            logger.error(f"STTThread 设置失败: {e}", exc_info=True)
            self.event_bus.publish("ERROR", {"message": f"STTThread 设置失败: {e}"})
            return False

    def run(self):
        """线程主循环。"""
        if not self._setup():
            logger.error("由于设置失败，STTThread 将不会运行。")
            return

        logger.info("STTThread 已启动，等待语音指令...")
        while not self.stop_event.is_set():
            try:
                event = self.event_queue.get(timeout=1)
                self._handle_event(event)
            except Empty:
                continue

        logger.info("STTThread 循环已结束。")

    def _handle_event(self, event):
        event_type = event.get("type")
        if event_type == "VOICE_COMMAND_DETECTED":
            data = event.get("data", {})
            audio_data = data.get("audio_data")
            if audio_data:
                self._process_audio(
                    audio_data=audio_data,
                    sample_rate=data.get("sample_rate", 16000),
                    channels=data.get("channels", 1),
                    sample_width=data.get("sample_width", 2),
                )
        elif event_type == "EXIT":
            self.stop()

    def _process_audio(
        self, audio_data: bytes, sample_rate: int, channels: int, sample_width: int
    ):
        logger.info("STTThread: 接收到音频数据，开始直接从内存处理...")
        stt_provider = self.config.get("stt_provider", "siliconflow").lower()

        try:
            recognized_text = ""
            if stt_provider == "siliconflow":
                # 将原始PCM数据包装在WAV头中，以便API可以识别
                # 这是必要的，因为API期望一个完整的文件格式，而不仅仅是原始样本
                import io
                buffer = io.BytesIO()
                with wave.open(buffer, "wb") as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(sample_width)
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_data)
                buffer.seek(0)
                wav_data = buffer.read()
                
                logger.info(f"调用 SiliconFlow STT API (内存)...")
                recognized_text = self.stt_client.speech_to_text(wav_data, audio_format="wav")

            elif stt_provider == "iflytek":
                # 讯飞的实现可以直接处理原始PCM数据流
                logger.info(f"调用 Iflytek STT API (内存)...")
                recognized_text = self.stt_client.speech_to_text(audio_data)

            if recognized_text:
                logger.info(f"识别结果: '{recognized_text}'")
                self.event_bus.publish("STT_RESULT_RECEIVED", {"text": recognized_text})
                self.event_bus.publish("INTERRUPTION_DETECTED", source=self.name)
            else:
                logger.warning("STT 未返回有效文本。")

        except Exception as e:
            logger.error(f"处理音频时发生错误: {e}", exc_info=True)
            self.event_bus.publish("ERROR", {"message": f"STT 处理失败: {e}"})

    def stop(self):
        """设置停止事件以终止线程。"""
        logger.info("正在停止 STTThread...")
        self.stop_event.set()


if __name__ == "__main__":
    # --- 用于测试 STTThread 的示例代码 ---
    # (此部分需要一个能产生VOICE_COMMAND_DETECTED事件的环境，因此集成测试更有效)
    print("STTThread 模块。请通过集成测试来验证其功能。")
    print("例如，运行 DeskRobot.py 并说话。")
