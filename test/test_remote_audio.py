from importmonkey import add_path

add_path("../../../../..")

from src.DeskRobot.util.config import config
from src.DeskRobot.voice.voice_interface import get_voice_interface


def test1():
    voice = get_voice_interface()
    text = voice.speech_to_text(5, save_audio=False)
    print(f"识别的文本: {text}")
    suc = voice.text_to_speech(text)
    print(f"播放结果: {suc}")


if __name__ == "__main__":
    config()
    test1()
