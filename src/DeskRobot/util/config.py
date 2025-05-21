from dotenv import load_dotenv

OLED_SCREEN_WIDTH = 128
OLED_SCREEN_HEIGHT = 64
OLED_FRAMERATE = 60
OLED_I2C_ADDRESS = 0x3C
OLED_CV_SIMULATION = False


PROJECT_ROOT = "/home/xe/Documents/code/final_project/DeskRobot"
SERVER_SRC_PATH = PROJECT_ROOT + "/src/DeskRobot/mcp_server.py"
DOTENV_PATH = PROJECT_ROOT + "/.env"


PIPER_PATH = PROJECT_ROOT + "/dn/piper/piper"
PIPER_MODEL_PATH = PROJECT_ROOT + "/dn/piper/model"
PIPER_VOICE = "zh_CN-huayan-x_low.onnx"
PIPER_OUTPUT_PATH = PROJECT_ROOT + "/dn/piper/output"


def config():
    load_dotenv(DOTENV_PATH)
