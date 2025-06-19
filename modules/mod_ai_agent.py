"""
AI 对话线程
负责监听用户输入事件，调用 AI API 获取回复，并发布待播报文本事件。

Subscribe:
- STT_RESULT_CAPTURED: 语音转文字结果
    - payload格式:
    {
        "text": str,  # 用户说话内容
        "confidence": float,  # 识别置信度（可选）
        "source": str  # 识别来源（可选）
    }
- STOP_THREADS: 停止线程

Publish:
- SUB_TEXT_STATIC_DISPLAY: 显示AI回复文本
    - 将AI回复内容显示到屏幕上
- TTS_REQUEST: 文字转语音请求（如果启用语音回复）
    - 将AI回复内容转为语音播放

"""

import logging
import threading
from queue import Empty, Queue

from modules.API_AI.ai_api import AiAPI  # AI API 接口
from modules.API_EventBus.event_bus import EventBus  # For type hinting

logger = logging.getLogger(__name__)


class AiThread(threading.Thread):
    def __init__(self, event_bus: EventBus,llm_base_url: str = None, llm_api_key: str = None, llm_model_name: str = None):
        super().__init__(daemon=True, name="AiThread")
        self.event_bus = event_bus
        self._stop_event = threading.Event()
        self.api = None
        self.llm_base_url = llm_base_url
        self.llm_api_key = llm_api_key
        self.llm_model_name = llm_model_name

        # 创建私有队列并订阅
        self.event_queue = Queue()
        self.event_bus.subscribe("STT_RESULT_CAPTURED", self.event_queue)
        self.event_bus.subscribe("STOP_THREADS", self.event_queue)

    def run(self):
        """线程主循环"""
        logger.info(f"{self.name} 启动，正在初始化 API...")
        self.event_bus.publish("THREAD_STARTED", name=self.__class__.__name__)

        try:
            # API的初始化可能比较耗时，所以在线程的run方法中执行
            self.api = AiAPI(
                llm_base_url=self.llm_base_url,
                llm_api_key=self.llm_api_key,
                llm_model_name=self.llm_model_name,
            )
        except Exception:
            logger.critical("AI API 初始化失败，线程即将退出。", exc_info=True)
            return

        logger.info("AI 线程初始化完成，开始监听事件。")
        while not self._stop_event.is_set():
            try:
                # 从自己的私有队列中获取事件
                event = self.event_queue.get(timeout=1)
                event_type = event.get("type")
                payload = event.get("payload", {})

                if event_type == "STOP_THREADS":
                    logger.debug(f"{self.name} 收到停止事件。")
                    break

                if event_type == "STT_RESULT_CAPTURED":
                    text = payload.get("text", "")
                    if text:
                        logger.info(f"接收到STT结果: '{text}'")
                        # 调用API获取回复
                        ai_response = self.api.get_response(text)

                        # 发布一个事件，让语音模块去播报
                        if ai_response:
                            logger.info(f"已发布TTS请求: '{ai_response}'")
                            self.event_bus.publish(
                                "SPEAK_TEXT",
                                source=self.__class__.__name__,
                                text=ai_response,
                            )

            except Empty:
                # 队列超时为空，是正常现象，继续循环
                continue
            except Exception:
                logger.error("AI 线程主循环发生错误", exc_info=True)

        logger.info(f"{self.name} 已停止。")

    def stop(self, **kwargs):
        """请求线程停止。"""
        logger.info(f"正在请求停止 {self.name}...")
        self._stop_event.set()
