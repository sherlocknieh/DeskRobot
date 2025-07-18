import logging
from typing import Dict, Optional
import os

logger = logging.getLogger("SileroVAD")

import numpy as np
logger.info("正在导入 torch...")
import torch

class SileroVAD:
    """
    一个围绕 Silero VAD 模型的包装类，用于实时语音活动检测。

    这个类使用 torch.hub 加载 Silero VAD 模型和工具。它提供了一个简单的接口
    来处理音频块，并使用 VADIterator 检测语音的开始和结束。
    """

    def __init__(self, threshold: float = 0.5, sample_rate: int = 16000):
        if sample_rate not in [8000, 16000]:
            raise ValueError("Silero VAD anly supports 8000 or 16000 sample rate.")
        
        local_model_path = os.path.expanduser("~/.cache/torch/hub/snakers4_silero-vad_master")
        use_local = os.path.exists(local_model_path)
        repo_or_dir = local_model_path if use_local else "snakers4/silero-vad"
        load_kwargs = {
            "repo_or_dir": repo_or_dir,
            "model": "silero_vad",
            "force_reload": False
        }
        if use_local:
            logger.info(f"正在从本地加载 Silero VAD 模型")
            load_kwargs["source"] = "local"
        else:
            logger.info(f"正在在线下载加载 Silero VAD 模型...")
            logger.info(f"如果下载速度过慢，可以浏览器手动下载,手动解压并保存为: {local_model_path}")
        try:
            model, utils = torch.hub.load(**load_kwargs)  # type: ignore
            (get_speech_timestamps,
                save_audio,
                read_audio,
                VADIterator,
                collect_chunks) = utils
            self.vad_iterator = VADIterator(model, threshold)
            logger.info(f"Silero VAD 模型{'本地' if use_local else '在线'}加载成功。")
        except Exception as e:
            logger.error(f"Silero VAD 模型加载失败: {e}", exc_info=True)
            raise


    def process_chunk(self, chunk: bytes) -> Optional[Dict]:
        """
        处理单个音频块并返回语音事件。

        :param chunk: 音频数据的字节流 (bytes)。应为16位整数格式。
        :return: 如果检测到语音开始或结束，则返回一个字典，否则返回 None。
                 例如: {'start': 12345} 或 {'end': 67890}
        """
        if not chunk:
            return None
        
        # 将 bytes 转换为 float32 tensor
        audio_int16 = np.frombuffer(chunk, np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0

        # 处理流式音频
        speech_dict = self.vad_iterator(audio_float32, return_seconds=False)

        return speech_dict


    def reset_states(self):
        """
        重置 VAD 迭代器的内部状态。
        在处理新的独立音频流时调用。
        """
        self.vad_iterator.reset_states()
        logger.info("Silero VAD 状态已重置。")


if __name__ == "__main__":
    import os
    import sys
    import wave

    # 将项目根目录添加到 sys.path，以解决模块导入问题
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    sys.path.insert(0, project_root)
    from modules.API_Voice.IO.io import VoiceIO
    sys.path.pop(0)


    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # --- 配置 ---
    # Silero VAD 模型在 16kHz 采样率下期望的帧大小为 512。
    # 不要使用其他值，否则会引发模型内部错误。
    # (512 samples / 16000 Hz = 32 ms)
    SAMPLE_RATE = 16000
    FRAMES_PER_BUFFER = 512
    CHANNELS = 1
    RECORD_SECONDS = 15

    # --- 初始化 ---
    voice_io = None
    try:
        voice_io = VoiceIO(
            rate=SAMPLE_RATE,
            frames_per_buffer=FRAMES_PER_BUFFER,
            channels=CHANNELS
        )
        vad = SileroVAD(sample_rate=SAMPLE_RATE)

        print("\n" + "=" * 50)
        print(f"测试开始，将运行 {RECORD_SECONDS} 秒。请在安静时说话。")
        print("=" * 50 + "\n")

        is_speaking = False
        speech_frames = []
        file_counter = 0

        num_loops = int(SAMPLE_RATE / FRAMES_PER_BUFFER * RECORD_SECONDS)

        for i in range(num_loops):
            chunk = voice_io.record_chunk()
            event = vad.process_chunk(chunk)

            if event:
                if "start" in event and not is_speaking:
                    is_speaking = True
                    print(f"检测到语音开始 (chunk {i})")
                    speech_frames = [chunk]  # 开始新的录音
                elif "end" in event and is_speaking:
                    is_speaking = False
                    speech_frames.append(chunk)
                    print(f"检测到语音结束 (chunk {i})")

                    # 保存音频
                    filename = f"vad_test_output_{file_counter}.wav"
                    with wave.open(filename, "wb") as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(voice_io.p.get_sample_size(voice_io.format)) # type: ignore
                        wf.setframerate(SAMPLE_RATE)
                        wf.writeframes(b"".join(speech_frames))
                    print(f"语音已保存到: {filename}")

                    file_counter += 1
                    speech_frames = []
            elif is_speaking:
                speech_frames.append(chunk)

        print("\n" + "=" * 50)
        print("测试结束。")
        print("=" * 50)

    except Exception as e:
        logger.error(f"VAD 测试时发生错误: {e}", exc_info=True)
    finally:
        if voice_io:
            voice_io.close()
