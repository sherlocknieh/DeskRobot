from importmonkey import add_path

add_path("../../../../..")
from src.DeskRobot.voice.piper_tts import get_piper_tts


def main():
    # Initialize the TTS engine
    tts = get_piper_tts()

    # Define the text to be spoken
    text = "Hello, I am Desk Robot. How can I assist you today?"

    # Speak the text
    audio_path = tts.text_to_speech(text)
    print(f"Audio saved to: {audio_path}")


if __name__ == "__main__":
    main()
