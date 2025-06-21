"""
AI Agent 线程，是整个机器人对话交互的大脑。

本线程负责编排整个对话流程，管理机器人的内部状态（思考、说话、闲置），
并确保动作、表情与语音的精确同步。

主要职责:
1.  接收语音识别（STT）结果，启动思考流程。
2.  在思考时，通过事件控制机器人进入“专注思考”状态（如闭眼、显示思考动画）。
3.  调用 AI API，获取语言回复和需要伴随语音执行的动作（如做表情）。
4.  将语言回复发送给 TTS 模块进行播报。
5.  在 TTS 开始播报的瞬间，执行所有伴随动作，并让机器人恢复“专注诉说”状态（如睁眼）。
6.  在 TTS 播报结束后，根据结束状态（正常完成或被打断）决定是否让机器人进入“闲置”状态。

---------------------------------------------------------------------

订阅 (Subscribe):
- STT_RESULT_RECEIVED: 接收到语音转文字结果，这是驱动AI思考的主要入口。
    - payload: {"text": str}
- TTS_STARTED: 监听到语音开始播放。用于精确同步动作和表情。
- TTS_FINISHED: 监听到语音播放完毕。用于判断是否应恢复闲置状态。
    - payload: {"interrupted": bool} (可选)
- STOP_THREADS: 停止线程。

发布 (Publish):
- SPEAK_TEXT: 请求 TTS 模块合成并播放语音。
    - payload: {"text": str}
- START_AI_THINKING / STOP_AI_THINKING: 控制思考动画的开始和结束。
- DISABLE_IDLE_MODE / ENABLE_IDLE_MODE: 控制机器人闲置行为（如晃动）的开关。
- CENTER_EYES: 控制机器人眼睛居中，以示专注。
- DISABLE_AUTOBLINKER / ENABLE_AUTOBLINKER: 控制自动眨眼的开关。
- OPEN_EYES / CLOSE_EYES: 控制眼睛的开合。
- SET_EXPRESSION / TRIGGER_QUICK_EXPRESSION: （通过 actions_on_speak 间接发布）设置或触发表情。

"""

import logging
import queue
import threading
import traceback

from modules.API_AI.ai_api import AiAPI  # AI API 接口
from modules.EventBus.event_bus import EventBus  # For type hinting

logger = logging.getLogger(__name__)


class AiThread(threading.Thread):
    def __init__(
        self,
        event_bus: EventBus,
        llm_base_url: str,
        llm_api_key: str,
        llm_model_name: str,
    ):
        super().__init__()
        self.name = self.__class__.__name__
        self.event_bus = event_bus
        self.event_queue = queue.Queue()
        self.api = None  # 在 run 方法中初始化
        self._stop_event = threading.Event()  # 用于优雅地停止线程

        # 保存LLM配置以备后用
        self.llm_base_url = llm_base_url
        self.llm_api_key = llm_api_key
        self.llm_model_name = llm_model_name
        self.actions_on_speak = []  # 新增：用于暂存待执行的动作

        self.event_bus.subscribe("STT_RESULT_RECEIVED", self.event_queue, self.name)
        self.event_bus.subscribe("TTS_STARTED", self.event_queue, self.name)
        self.event_bus.subscribe("TTS_FINISHED", self.event_queue, self.name)
        self.event_bus.subscribe("STOP_THREADS", self.event_queue, self.name)

    def run(self):
        """线程主循环"""
        logger.info("AiThread 启动，正在初始化 API...")
        self.event_bus.publish("THREAD_STARTED", name=self.__class__.__name__)

        try:
            self.api = AiAPI(
                event_bus=self.event_bus,
                llm_base_url=self.llm_base_url,
                llm_api_key=self.llm_api_key,
                llm_model_name=self.llm_model_name,
            )
        except Exception as e:
            logger.critical(f"AI API 初始化失败，线程即将退出。错误: {e}")
            traceback.print_exc()
            return

        logger.info("AI 线程初始化完成，开始监听事件。")
        while not self._stop_event.is_set():
            try:
                # 从自己的私有队列中获取事件
                event = self.event_queue.get(timeout=1)
                event_type = event.get("type")
                payload = event.get("payload", {})

                if event_type == "STOP_THREADS":
                    logger.info(f"{self.name} 接到停止指令，正在退出...")
                    self._stop_event.set()
                    break

                if event_type == "STT_RESULT_RECEIVED":
                    text = payload.get("text")
                    if text:
                        # --- 开始调用AI ---
                        logger.info(f"正在为 STT 结果调用 AI: '{text}'")

                        # 1. 发布“开始思考”事件，触发思考动画和表情
                        self.event_bus.publish("START_AI_THINKING", source=self.name)
                        self.event_bus.publish("DISABLE_IDLE_MODE", source=self.name)
                        self.event_bus.publish("CENTER_EYES", source=self.name)
                        self.event_bus.publish("DISABLE_AUTOBLINKER", source=self.name)
                        self.event_bus.publish("CLOSE_EYES", source=self.name)

                        # 2. 调用AI获取回复 (这会阻塞)
                        response_text, queued_actions = self.api.get_response(
                            text, thread_id="user_session"
                        )
                        # 暂存待执行的动作
                        self.actions_on_speak = queued_actions

                        if response_text:
                            # 3. 发布TTS事件，让机器人说话
                            self.event_bus.publish(
                                "SPEAK_TEXT", text=response_text, source=self.name
                            )
                        else:
                            # 如果没有回复，也要停止思考动画并恢复状态
                            self.event_bus.publish("STOP_AI_THINKING", source=self.name)
                            self.event_bus.publish("OPEN_EYES", source=self.name)
                            self.event_bus.publish(
                                "ENABLE_AUTOBLINKER", source=self.name
                            )
                            self.event_bus.publish("ENABLE_IDLE_MODE", source=self.name)

                elif event_type == "TTS_STARTED":
                    # 语音播放开始时，停止思考动画并恢复表情
                    self.event_bus.publish("STOP_AI_THINKING", source=self.name)
                    self.event_bus.publish("OPEN_EYES", source=self.name)
                    self.event_bus.publish("ENABLE_AUTOBLINKER", source=self.name)

                    # --- 关键改动 ---
                    # 在开口说话的瞬间，执行暂存的动作
                    if self.actions_on_speak:
                        logger.info(
                            f"正在执行 {len(self.actions_on_speak)} 个暂存的动作..."
                        )
                        for action in self.actions_on_speak:
                            self.event_bus.publish(action["type"], **action["payload"])
                        self.actions_on_speak = []  # 执行后清空

                elif event_type == "TTS_FINISHED":
                    # 语音播放结束后，根据是否被打断来决定是否恢复闲置
                    interrupted = payload.get("interrupted", False)
                    if interrupted:
                        # TTS被用户打断，机器人应保持专注，等待新指令
                        logger.info("语音播放被打断，保持专注等待新指令。")
                    else:
                        # TTS正常播放完成，可以恢复闲置模式
                        logger.info("语音播放结束，恢复闲置模式。")
                        self.event_bus.publish("ENABLE_IDLE_MODE", source=self.name)

            except queue.Empty:
                # 队列超时为空，是正常现象，继续循环
                continue
            except Exception:
                logger.error("AI 线程主循环发生错误", exc_info=True)

        logger.info(f"{self.name} 已停止。")

    def stop(self, **kwargs):
        """请求线程停止。"""
        logger.info(f"正在请求停止 {self.name}...")
        self._stop_event.set()
