"""
语音处理与语音活动检测(VAD)模块。

本模块是机器人系统的“耳朵”，它持续监听麦克风，并根据机器人的状态（是否正在说话）
来智能地处理用户的语音输入。

核心功能:
- 持续从麦克风读取音频流。
- 使用 SileroVAD 进行语音活动检测，判断用户是否在说话。
- 具备双重状态模式：
  1.  **聆听模式**: 当机器人自身未在说话时，它会录制用户的完整一句话，
      并将其作为 `VOICE_COMMAND_DETECTED` 事件发布出去。
  2.  **打断模式**: 当机器人正在说话时（通过监听 `TTS_STARTED` 和 `TTS_FINISHED`
      事件得知），它会将用户的任何语音输入视为一次“打断”。此时，它会立即
      发布 `INTERRUPTION_DETECTED` 事件（用于通知TTS模块停止播放），然后
      无缝切换到“聆听模式”，开始录制用户的“打断”内容，并最终同样发布
      `VOICE_COMMAND_DETECTED` 事件。

这种设计使得用户打断交互变得无缝且自然。

---------------------------------------------------------------------

订阅 (Subscribe):
- TTS_STARTED: 当 TTS 开始播放时，进入“打断模式”。
- TTS_FINISHED: 当 TTS 结束播放时，回到“聆- 听模式”。
- STOP_THREADS: 停止线程。

发布 (Publish):
- VOICE_COMMAND_DETECTED: 当检测到一段完整的用户语音时发布（无论是正常聆听还是打断）。
    - payload: {"audio_data": bytes, "sample_rate": int, "channels": int, "sample_width": int}
- INTERRUPTION_DETECTED: 在“打断模式”下，检测到用户语音的瞬间发布，用于立即停止TTS。

"""

import logging
import threading
import time
from queue import Queue

from .API_Voice.IO.io import VoiceIO
from .API_Voice.VAD.vad import SileroVAD
from .EventBus import EventBus

logger = logging.getLogger(__name__)


class VoiceThread(threading.Thread):
    """
    一个集成了音频IO和语音活动检测（VAD）的独立线程。

    该线程负责以下任务：
    - 通过 VoiceIO 持续从麦克风读取音频数据。
    - 使用 SileroVAD 分析音频流，以检测语音的开始和结束。
    - 当检测到完整的语音片段（一句话）时，将该片段的音频数据
      通过 EventBus 发布。
    - 监听 "STOP_THREADS" 事件以实现优雅关闭。

    subscribe:
    - TTS_STARTED: TTS 开始播放
    - TTS_FINISHED: TTS 结束播放
    - STOP_THREADS: 停止线程。

    publish:
    - VOICE_COMMAND_DETECTED: 当检测到完整的语音指令时发布。
        - payload: {"audio_data": bytes, "sample_rate": int, "channels": int, "sample_width": int}
    - INTERRUPTION_DETECTED: 当TTS播放时检测到用户语音（打断）时发布。
    """

    def __init__(
        self,
        event_bus: EventBus,
        sample_rate: int,
        channels: int,
        vad_threshold: float,
        frames_per_buffer: int,
    ):
        """
        初始化 VoiceThread。

        :param event_bus: 事件总线实例，用于模块间通信。
        :param sample_rate: 音频采样率。必须与VAD模型期望的速率匹配。
        :param channels: 音频通道数。
        :param vad_threshold: VAD 灵敏度阈值 (0-1)。
        :param frames_per_buffer: 每个音频块的帧数。
        """
        super().__init__()
        self.daemon = True
        self.name = "Voice Thread"
        self.event_bus = event_bus
        self.stop_event = threading.Event()
        self.event_queue = Queue()

        self.sample_rate = sample_rate
        self.channels = channels
        self.vad_threshold = vad_threshold
        self.frames_per_buffer = frames_per_buffer

        self.voice_io = None
        self.vad = None

        self.is_speaking_tts = False  # 新增：用于跟踪TTS播放状态
        self.is_detecting_speech = False  # 新增：用于跟踪VAD检测状态
        self.speech_frames = []

        logger.info("VoiceThread 初始化完成。")

    def _setup(self):
        """初始化音频IO和VAD实例。"""
        try:
            logger.info("正在设置 VoiceThread 的底层组件...")
            self.voice_io = VoiceIO(
                rate=self.sample_rate,
                channels=self.channels,
                frames_per_buffer=self.frames_per_buffer,
            )
            self.vad = SileroVAD(
                sample_rate=self.sample_rate, threshold=self.vad_threshold
            )
            self.event_bus.subscribe("STOP_THREADS", self.event_queue)
            self.event_bus.subscribe("TTS_STARTED", self.event_queue)
            self.event_bus.subscribe("TTS_FINISHED", self.event_queue)
            logger.info("VoiceThread 底层组件设置成功。")
            return True
        except Exception as e:
            logger.error(f"VoiceThread 设置失败: {e}", exc_info=True)
            return False

    def run(self):
        """线程主循环。"""
        if not self._setup():
            logger.error("由于设置失败，VoiceThread 将不会运行。")
            return

        logger.info("VoiceThread 已启动，开始监听麦克风...")

        while not self.stop_event.is_set():
            self._handle_events()  # 处理来自总线的事件

            chunk = self.voice_io.record_chunk()
            if not chunk:
                time.sleep(0.01)
                continue

            vad_event = self.vad.process_chunk(chunk)

            if self.is_speaking_tts:
                # 在TTS播放期间，只关心语音的开始，这表示打断
                if vad_event and "start" in vad_event:
                    logger.info("在TTS播放期间检测到语音，触发打断并开始录制新指令...")
                    # 1. 发布打断事件，让TTS停止
                    self.event_bus.publish("INTERRUPTION_DETECTED")
                    # 2. 立即切换到正常的语音检测模式
                    self.is_speaking_tts = False
                    self.is_detecting_speech = True
                    self.speech_frames = [chunk]
                    # 后续的循环将自动像正常检测一样处理语音结束和发布
            else:
                # 正常语音检测逻辑
                if vad_event:
                    if "start" in vad_event and not self.is_detecting_speech:
                        self.is_detecting_speech = True
                        logger.info("检测到语音开始...")
                        self.speech_frames = [chunk]
                    elif "end" in vad_event and self.is_detecting_speech:
                        self.is_detecting_speech = False
                        self.speech_frames.append(chunk)
                        logger.info("检测到语音结束。正在发布事件...")

                        full_speech_audio = b"".join(self.speech_frames)
                        self.speech_frames = []

                        self.event_bus.publish(
                            "VOICE_COMMAND_DETECTED",
                            audio_data=full_speech_audio,
                            sample_rate=self.sample_rate,
                            channels=self.channels,
                            sample_width=self.voice_io.p.get_sample_size(
                                self.voice_io.format
                            ),
                        )
                elif self.is_detecting_speech:
                    self.speech_frames.append(chunk)

        logger.info("VoiceThread 循环已结束。")
        self._cleanup()

    def _handle_events(self):
        """处理来自事件总线的事件，用于更新内部状态。"""
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                if event["type"] == "STOP_THREADS":
                    self.stop()
                elif event["type"] == "TTS_STARTED":
                    self.is_speaking_tts = True
                    # TTS开始时，如果正在检测语音，应取消
                    if self.is_detecting_speech:
                        logger.info("TTS开始，取消当前的语音检测。")
                        self.is_detecting_speech = False
                        self.speech_frames = []
                elif event["type"] == "TTS_FINISHED":
                    self.is_speaking_tts = False
        except Queue.Empty:
            pass  # 队列为空是正常情况

    def stop(self):
        """设置停止事件以终止线程。"""
        logger.info("正在停止 VoiceThread...")
        self.stop_event.set()

    def _cleanup(self):
        """清理资源。"""
        logger.info("正在清理 VoiceThread 资源...")
        if self.voice_io:
            self.voice_io.close()
        logger.info("VoiceThread 已成功清理并停止。")


if __name__ == "__main__":
    # --- 用于测试 VoiceThread 的示例代码 ---
    import os
    import queue
    import sys
    import wave

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from modules.EventBus import EventBus

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # --- 启动测试 ---
    eb = EventBus()

    # 创建一个队列来接收语音事件
    voice_event_queue = queue.Queue()
    eb.subscribe("VOICE_COMMAND_DETECTED", voice_event_queue, "VoiceThread Tester")

    voice_thread = VoiceThread(eb)

    try:
        print("\n" + "=" * 50)
        print("VoiceThread 测试启动。请说话，每说完一句话，")
        print("系统会自动检测并保存为一个 .wav 文件。")
        print("按 Ctrl+C 结束测试。")
        print("=" * 50 + "\n")

        voice_thread.start()
        file_counter = 0

        # 主循环，监听队列并处理事件
        while voice_thread.is_alive():
            try:
                # 等待语音事件，设置超时以允许检查线程状态和Ctrl+C
                event = voice_event_queue.get(timeout=0.5)

                if event["type"] == "VOICE_COMMAND_DETECTED":
                    audio_data = event["payload"]["audio_data"]
                    logger.info(
                        f"Tester: 接收到语音命令，数据长度: {len(audio_data)} bytes。"
                    )

                    # 保存到文件以供验证
                    filename = f"voice_thread_test_{file_counter}.wav"
                    with wave.open(filename, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)  # 16-bit
                        wf.setframerate(16000)
                        wf.writeframes(audio_data)
                    logger.info(f"Tester: 语音已保存到 {filename}")
                    file_counter += 1

            except queue.Empty:
                # 队列为空是正常情况，继续循环
                continue

    except KeyboardInterrupt:
        print("\n检测到 Ctrl+C，正在优雅地关闭...")
        eb.publish("STOP_THREADS")
        voice_thread.join(timeout=5)
        print("测试结束。")
    except Exception as e:
        logger.error(f"测试主程序发生错误: {e}", exc_info=True)
        eb.publish("STOP_THREADS")
        voice_thread.join(timeout=5)
