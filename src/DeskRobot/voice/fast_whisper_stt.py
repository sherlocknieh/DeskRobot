# import union
from typing import Union

from faster_whisper import WhisperModel
from numpy import ndarray
from util.config import FAST_WHISPER_MODEL_PATH

__instance = None


class FastWhisperSTT:
    def __init__(
        self,
        model_size: str = "tiny",
        device: str = "cpu",
        download_root: str = FAST_WHISPER_MODEL_PATH,
    ):
        """
        Initialize the FastWhisperSTT class.
        """
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type="int8",
            download_root=download_root,
        )
        if not self.model:
            raise Exception(
                f"Failed to load Fast Whisper model from {download_root}. Please check the model path."
            )

    def speech_to_text(self, audio: Union[ndarray, str] = None):
        """
        Convert speech to text using Fast Whisper.
        :param audio: Audio data or path to the audio file.
        :return: Transcribed text.
        """
        segments, info = self.model.transcribe(audio=audio, beam_size=5)

        # print(
        #    "Detected language '%s' with probability %f"
        #     % (info.language, info.language_probability)
        #  )

        text = ""

        for segment in segments:
            text += segment.text
            print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
        return text


def get_fast_whisper_stt():
    """
    Get FastWhisperSTT instance.
    :return: FastWhisperSTT instance.
    """
    global __instance
    if __instance is None:
        __instance = FastWhisperSTT()
    return __instance
