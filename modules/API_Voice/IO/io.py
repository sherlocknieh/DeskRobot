import logging
import wave

import pyaudio

logger = logging.getLogger(__name__)


class VoiceIO:
    """
    负责处理所有与音频输入输出相关的底层操作。
    - 初始化和管理PyAudio音频流。
    - 提供从麦克风录制音频数据块的功能。
    - 提供播放音频数据块的功能。
    - 统一管理音频参数（采样率、通道数、格式）。
    """

    def __init__(
        self, rate=16000, channels=1, format=pyaudio.paInt16, frames_per_buffer=1024
    ):
        """
        初始化VoiceIO。

        :param rate: 采样率 (Hz)
        :param channels: 通道数
        :param format: 音频格式 (e.g., pyaudio.paInt16)
        :param frames_per_buffer: 每个缓冲区的帧数
        """
        self.rate = rate
        self.channels = channels
        self.format = format
        self.frames_per_buffer = frames_per_buffer
        self.p = None
        self.input_stream = None
        self.output_stream = None

        try:
            self._initialize_pyaudio()
            self._open_streams()
            logger.info("VoiceIO 初始化成功。")
        except Exception as e:
            logger.error(f"VoiceIO 初始化失败: {e}", exc_info=True)
            self.close()
            raise

    def _initialize_pyaudio(self):
        """初始化PyAudio实例。"""
        logger.info("正在初始化 PyAudio...")
        self.p = pyaudio.PyAudio()
        logger.info("PyAudio 初始化完成。")

    def _open_streams(self):
        """打开音频输入和输出流。"""
        logger.info("正在打开音频流...")

        # 获取默认设备信息
        default_input_device_info = self.p.get_default_input_device_info()
        default_output_device_info = self.p.get_default_output_device_info()

        input_device_index = default_input_device_info["index"]
        output_device_index = default_output_device_info["index"]

        logger.info(
            f"使用默认输入设备: {default_input_device_info['name']} (索引: {input_device_index})"
        )
        logger.info(
            f"使用默认输出设备: {default_output_device_info['name']} (索引: {output_device_index})"
        )

        self.input_stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
            input_device_index=input_device_index,
        )
        logger.info("音频输入流已打开。")

        self.output_stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.frames_per_buffer,
            output_device_index=output_device_index,
        )
        logger.info("音频输出流已打开。")

    def record_chunk(self) -> bytes:
        """
        从输入流录制一个音频数据块。

        :return: 音频数据 (bytes)
        """
        try:
            return self.input_stream.read(self.frames_per_buffer)
        except IOError as e:
            logger.error(f"录制音频时发生IO错误: {e}")
            # 返回静音数据以避免上层应用崩溃
            return (
                b"\x00"
                * self.frames_per_buffer
                * self.channels
                * pyaudio.get_sample_size(self.format)
            )

    def play_audio_chunk(self, chunk: bytes):
        """
        播放一个音频数据块。

        :param chunk: 要播放的音频数据 (bytes)
        """
        if self.output_stream:
            self.output_stream.write(chunk)

    def close(self):
        """关闭所有音频流并终止PyAudio。"""
        logger.info("正在关闭 VoiceIO...")
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            logger.info("输入流已关闭。")
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            logger.info("输出流已关闭。")
        if self.p:
            self.p.terminate()
            logger.info("PyAudio 已终止。")
        self.input_stream = self.output_stream = self.p = None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        voice_io = VoiceIO()

        print("\n准备录音... 请在麦克风前说话。录音将持续5秒。")

        frames = []
        for _ in range(0, int(16000 / 1024 * 5)):
            data = voice_io.record_chunk()
            frames.append(data)

        print("录音结束。")

        # 保存到文件
        wf = wave.open("test_recording.wav", "wb")
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b"".join(frames))
        wf.close()
        print("录音已保存到 test_recording.wav")

        print("\n现在播放录音...")
        for data in frames:
            voice_io.play_audio_chunk(data)
        print("播放结束。")

    except Exception as e:
        logger.error(f"主程序发生错误: {e}", exc_info=True)
    finally:
        if "voice_io" in locals() and voice_io:
            voice_io.close()

    print("\n程序结束。")
