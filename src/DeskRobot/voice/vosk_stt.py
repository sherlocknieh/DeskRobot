import json
import sys
import wave

import numpy as np
from util.config import VOSK_MODEL, VOSK_MODEL_PATH
from vosk import KaldiRecognizer, Model, SetLogLevel

__instance = None


class VoskSTT:
    def __init__(self):
        self.model = Model(model_path=VOSK_MODEL_PATH + "/" + VOSK_MODEL)

        if not self.model:
            raise Exception(
                f"Failed to load Vosk model from {VOSK_MODEL_PATH}. Please check the model path."
            )

        SetLogLevel(0)

    def speech_to_text(self, audio_data=None, frame_rate=None, audio_path=None):
        if audio_data is None or frame_rate is None:
            wf = wave.open(audio_path, "rb")
            if (
                wf.getnchannels() != 1
                or wf.getsampwidth() != 2
                or wf.getcomptype() != "NONE"
            ):
                print("Audio file must be WAV format mono PCM.")
                sys.exit(1)
            params = wf.getparams()
            audio_data = np.frombuffer(wf.readframes(params.nframes), dtype=np.int16)
            frame_rate = params.framerate

        rec = KaldiRecognizer(self.model, frame_rate)
        rec.SetWords(True)

        res = json.loads(rec.FinalResult())
        print(res)
        return res["text"]


def get_vosk_stt():
    """
    获取VoskSTT实例
    :return: VoskSTT实例
    """
    global __instance
    if __instance is None:
        __instance = VoskSTT()
    return __instance
