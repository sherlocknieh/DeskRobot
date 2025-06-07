
from voice.fast_whisper_stt import get_fast_whisper_stt
from voice.piper_tts import get_piper_tts
from voice.voice_interface import get_voice_interface

# SetLogLevel(0)


def whisper_test():
    stt = get_fast_whisper_stt
    res = stt.speech_to_text(
        audio_path=PROJECT_ROOT + "/src/DeskRobot/recorded_audio.wav"
    )
    print(res)


def piper_test():
    # Initialize the TTS engine
    tts = get_piper_tts()

    # Define the text to be spoken
    text = "你好啊，我是一个桌面机器人。我的名字叫做小白。今天我能为你做些什么？"

    # Speak the text
    audio_path = tts.text_to_speech(text)
    print(f"Audio saved to: {audio_path}")


def remote_audio_test():
    config()
    # Initialize the voice interface
    voice = get_voice_interface()

    # Define the text to be spoken
    text = "你好，我是桌面机器人。今天我能为你做些什么？"

    # Speak the text
    audio_path = voice.text_to_speech(text)
    print(f"Audio saved to: {audio_path}")

    # Recognize speech
    recognized_text = voice.speech_to_text(5, save_audio=True)
    print(f"Recognized text: {recognized_text}")


if __name__ == "__main__":
    config()
    # piper_test()
    # vosk_test()
    # whisper_test()
    remote_audio_test()
