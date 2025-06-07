# import union
from typing import Union

from faster_whisper import WhisperModel
from numpy import ndarray

FAST_WHISPER_MODEL_PATH = "downloads"

_instance = None  # Changed from __instance


class FastWhisperSTT:
    def __init__(
        self,
        model_size: str = "tiny",
        device: str = "cpu",
        download_root: str = FAST_WHISPER_MODEL_PATH,
    ):
        """
        Initialize the FastWhisperSTT class.
        Ensures that only one instance of FastWhisperSTT is created.
        """
        global _instance
        if _instance is not None:
            raise RuntimeError(
                "Attempted to create multiple instances of FastWhisperSTT. "
                "Please use FastWhisperSTT.get_instance() to get the existing instance."
            )

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

    @staticmethod
    def get_instance(
        model_size: str = "tiny",
        device: str = "cpu",
        download_root: str = FAST_WHISPER_MODEL_PATH,
    ):
        """
        Get the FastWhisperSTT singleton instance.

        Args:
            model_size (str, optional): The model size to use. Defaults to "tiny".
            device (str, optional): The device to run the model on. Defaults to "cpu".
            download_root (str, optional): The root directory for model downloads. Defaults to FAST_WHISPER_MODEL_PATH.

        Returns:
            FastWhisperSTT: The singleton instance of FastWhisperSTT.
        """
        global _instance
        if _instance is None:
            _instance = FastWhisperSTT(
                model_size=model_size, device=device, download_root=download_root
            )
        return _instance
