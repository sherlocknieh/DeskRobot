"""
文本转语音（TTS）处理线程。

这是一个健壮的、可中断的、非阻塞的TTS模块。它负责将文本高效地转换为语音并播放，
同时能响应外部事件（如用户打断），并精确地报告其状态。

核心功能:
- 接收文本并调用 `EdgeTTS` 服务生成 `.mp3` 音频。
- 使用 `ffplay` 在后台非阻塞地播放音频。
- 能够被 `INTERRUPTION_DETECTED` 事件随时打断，并立即停止播放。
- 播放结束后，无论是正常完成还是被打断，都会发布 `TTS_FINISHED` 事件。
- 具备带重试逻辑的临时文件清理机制，确保在各种平台下都能可靠工作。

---------------------------------------------------------------------

订阅 (Subscribe):
- SPEAK_TEXT: 接收到需要播报的文本时触发。
    - data: {"text": str}
- INTERRUPTION_DETECTED: 接收到打断信号时触发，会立即停止当前播放。
- EXIT: 停止线程。

发布 (Publish):
- TTS_STARTED: 在音频文件生成完毕、即将开始播放时发布。
- TTS_FINISHED: 在音频播放结束后发布（无论是正常结束还是被中途打断）。
    - data: {"interrupted": True} (仅在被中途打断时携带此载荷)

"""

import logging
import os
import subprocess
import tempfile
import threading
import time
from queue import Empty, Queue

from pydub.utils import get_player_name

from .API_Voice.TTS.edge_tts1 import EdgeTTS
from .EventBus import EventBus

logger = logging.getLogger("TTS 模块")


class TTSThread(threading.Thread):
    """
    文本转语音（TTS）处理线程。

    该线程负责将文本转换为语音并播放。

    subscribe:
    - SPEAK_TEXT: 接收到需要播报的文本时触发。
        - data: {"text": str}
    - INTERRUPTION_DETECTED: 检测到音频播放中断时触发。
    - EXIT: 停止线程。

    publish:
    - TTS_STARTED: 开始播放语音时发布。
    - TTS_FINISHED: 结束播放语音时发布。
    """

    def __init__(self):
        super().__init__(daemon=True, name="TTS 模块")
        self.event_bus = EventBus()
        self.event_queue = Queue()
        self.stop_event = threading.Event()
        self.playback_handle = None  # 用于跟踪播放进程
        self.temp_audio_file_path = None  # 用于跟踪临时音频文件

        self.tts_client = EdgeTTS()
        # 注意：这里我们不直接使用VoiceIO，因为播放功能更适合封装在TTS API内部
        # 或者使用一个更简单的播放库，以避免管理复杂的PyAudio流。
        # 我们将使用pydub的播放功能。

        logger.info("TTSThread 初始化完成。")

    def _setup(self):
        """订阅事件。"""
        try:
            self.event_bus.subscribe("SPEAK_TEXT", self.event_queue, self.name)
            self.event_bus.subscribe("INTERRUPTION_DETECTED", self.event_queue, self.name)
            self.event_bus.subscribe("EXIT", self.event_queue, self.name)
            logger.info("TTSThread 事件订阅成功。")
            return True
        except Exception as e:
            logger.error(f"TTSThread 设置失败: {e}", exc_info=True)
            return False

    def run(self):
        """线程主循环。"""
        if not self._setup():
            return

        logger.info("TTSThread 已启动，等待文本转语音请求...")
        while not self.stop_event.is_set():
            try:
                event = self.event_queue.get(
                    timeout=0.1
                )  # 使用短暂超时以保持循环的响应性
                self._handle_event(event)
            except Empty:
                pass  # 超时后继续执行，以检查播放状态

            # 检查播放是否已结束
            if self.playback_handle and self.playback_handle.poll() is not None:
                # poll() 在进程结束时返回退出码，否则返回 None
                logger.info("TTS 音频播放完成。")
                self.event_bus.publish("TTS_FINISHED")
                self._cleanup_playback()

        logger.info("TTSThread 循环已结束。")

    def _handle_event(self, event):
        event_type = event.get("type")
        if event_type == "SPEAK_TEXT":
            text_to_speak = event.get("data", {}).get("text")
            if text_to_speak:
                self._process_text(text_to_speak)
        elif event_type == "INTERRUPTION_DETECTED":
            logger.info("TTSThread 收到打断事件，停止播放...")
            self._interrupt_playback()
        elif event_type == "EXIT":
            self.stop()

    def _cleanup_playback(self):
        """清理播放句柄和临时文件，带重试机制"""
        self.playback_handle = None
        if self.temp_audio_file_path:
            # ffplay 进程在 Windows 上可能不会立即释放文件句柄，
            # 因此我们添加一个短暂的重试循环来删除文件。
            for i in range(5):  # 重试5次
                try:
                    os.remove(self.temp_audio_file_path) # type: ignore
                    logger.info(f"已删除TTS临时文件: {self.temp_audio_file_path}")
                    self.temp_audio_file_path = None
                    return  # 删除成功，退出函数
                except OSError as e:
                    if i < 4:  # 如果不是最后一次尝试
                        logger.warning(
                            f"删除TTS临时文件失败 (尝试 {i + 1}/5): {e}。0.1秒后重试..."
                        )
                        time.sleep(0.1)
                    else:  # 最后一次尝试仍然失败
                        logger.error(f"删除TTS临时文件失败: {e}")
            self.temp_audio_file_path = None  # 即使删除失败，也要清空路径

    def _interrupt_playback(self):
        """如果当前有音频在播放，则中断它。"""
        if hasattr(self, "playback_handle") and self.playback_handle:
            if self.playback_handle.poll() is None:  # 进程仍在运行
                logger.info("正在中断当前 TTS 播放...")
                self.playback_handle.terminate()
                self.playback_handle.wait()  # 等待进程完全终止
                logger.info("TTS 播放已中断。")
                # 发布一个被中断的结束事件
                self.event_bus.publish("TTS_FINISHED", data={"interrupted": True})
            self._cleanup_playback()

    def _process_text(self, text: str):
        logger.info(f"TTSThread: 接收到文本 '{text}'，开始处理...")

        # 先中断任何可能正在播放的音频
        self._interrupt_playback()

        # 我们将自己管理临时文件，所以不用 with 语句的自动删除
        tmp_file = None
        try:
            # 1. 使用 EdgeTTS 生成 MP3 文件
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tmp_file_path = self.tts_client.text_to_speech_mp3(
                text, output_path=tmp_file.name
            )
            tmp_file.close()  # 关闭文件句柄

            if tmp_file_path:
                logger.info(f"TTS 音频已生成: {tmp_file_path}")
                self.event_bus.publish("TTS_STARTED", self.name)
                self.temp_audio_file_path = tmp_file_path

                # 2. 直接使用 ffplay 播放 MP3 文件，绕过 pydub 的播放问题
                player = get_player_name()
                self.playback_handle = subprocess.Popen(
                    [player, "-nodisp", "-autoexit", "-hide_banner", tmp_file_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            else:
                logger.error("TTS未能生成音频文件。")
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)

        except Exception as e:
            logger.error(f"处理文本转语音时发生错误: {e}", exc_info=True)
            # 如果出错，也尝试清理临时文件
            if tmp_file and os.path.exists(tmp_file.name):
                os.remove(tmp_file.name)

    def stop(self):
        """设置停止事件以终止线程。"""
        logger.info("正在停止 TTSThread...")
        self._interrupt_playback()
        self.stop_event.set()
