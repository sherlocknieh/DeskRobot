from dotenv import load_dotenv

OLED_SCREEN_WIDTH = 128
OLED_SCREEN_HEIGHT = 64
OLED_FRAMERATE = 50
OLED_I2C_ADDRESS = 0x3C
OLED_CV_SIMULATION = False


PROJECT_ROOT = "/home/xe/Documents/code/final_project/DeskRobot"
SERVER_SRC_PATH = PROJECT_ROOT + "/src/DeskRobot/mcp_server.py"
DOTENV_PATH = PROJECT_ROOT + "/.env"


PIPER_PATH = PROJECT_ROOT + "/dn/piper/piper"
PIPER_MODEL_PATH = PROJECT_ROOT + "/dn/piper/model"
PIPER_VOICE = "zh_CN-huayan-x_low.onnx"
PIPER_OUTPUT_PATH = PROJECT_ROOT + "/dn/piper/output"

VOSK_PATH = PROJECT_ROOT + "/dn/vosk"
VOSK_MODEL_PATH = VOSK_PATH + "/model"
VOSK_MODEL = "vosk-model-small-cn-0.22"

FAST_WHISPER_PATH = PROJECT_ROOT + "/dn/fast-whisper"
FAST_WHISPER_MODEL_PATH = FAST_WHISPER_PATH + "/model"


def config():
    load_dotenv(DOTENV_PATH)
