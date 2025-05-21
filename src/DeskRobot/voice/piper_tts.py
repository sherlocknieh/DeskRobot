import os

from util.config import PIPER_MODEL_PATH, PIPER_OUTPUT_PATH, PIPER_PATH, PIPER_VOICE

__instance = None


class PiperTTS:
    """
    Piper TTS (Text-to-Speech) class
    """

    def __init__(self, voice=PIPER_VOICE):
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
        res = os.system(command)
        if res != 0:
            print(f"Error: {res}")
            return None
        return self.audio_path


def get_piper_tts():
    """
    Get the Piper TTS instance
    :return: PiperTTS instance
    """
    global __instance
    if __instance is None:
        __instance = PiperTTS()
    return __instance
