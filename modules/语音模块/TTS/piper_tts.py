import os
import subprocess

from util.config import PIPER_MODEL_PATH, PIPER_OUTPUT_PATH, PIPER_PATH, PIPER_VOICE

_instance = None


class PiperTTS:
    """
    Piper TTS (Text-to-Speech) class
    """

    def __init__(self, voice=PIPER_VOICE):
        """
        Initialize the PiperTTS class.
        Ensures that only one instance of PiperTTS is created.
        """
        global _instance
        if _instance is not None:
            raise RuntimeError(
                "Attempted to create multiple instances of PiperTTS. "
                "Please use PiperTTS.get_instance() to get the existing instance."
            )

        self.voice = voice
        self.output_path = PIPER_OUTPUT_PATH
        self.model_path = PIPER_MODEL_PATH
        self.piper_path = PIPER_PATH

        # 创建输出目录
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        self.audio_path = os.path.join(self.output_path, "output.wav")

    def text_to_speech(self, text):
        """
        Convert text to speech using Piper TTS
        :param text: Text to convert
        :return: Path to the output audio file
        """
        # 使用Piper进行TTS
        command = f'echo  "{text}" | {self.piper_path}/piper --model {self.model_path}/{self.voice} --output_file {self.audio_path}'
        res = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if res.returncode != 0:
            print(f"Error: {res.stderr}")
            return None
        return self.audio_path

    @staticmethod
    def get_instance(voice=PIPER_VOICE):
        """
        Get the PiperTTS singleton instance.

        Args:
            voice (str, optional): The voice model to use. Defaults to PIPER_VOICE.

        Returns:
            PiperTTS: The singleton instance of PiperTTS.
        """
        global _instance
        if _instance is None:
            _instance = PiperTTS(voice=voice)
        return _instance
