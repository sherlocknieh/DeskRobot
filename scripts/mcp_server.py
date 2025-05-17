# use stdio_client function to spwan a process in client.py
from mcp.server.fastmcp import FastMCP
#from gpiozero import
from roboeyes import *
from roboeyes_thread import roboeyes
from roboeyes_thread import run as run_roboeyes, join as join_roboeyes

from gpiozero import RGBLED

mcp = FastMCP("testServer")
led = RGBLED(2,3,4)

@mcp.tool()
def setRobotEmotion(emotion: str) -> str:
    """根据输入的情感值，设置机器人的情感
    :param emotion: 输入的情感值:DEFAULT, HAPPY, TIRED, ANGRY
    :return: 返回设置的情感值
    """
    print("test")
    if emotion == "DEFAULT":
        roboeyes.set_mood(DEFAULT)
    elif emotion == "HAPPY":
        roboeyes.set_mood(HAPPY)
    elif emotion == "TIRED":
        roboeyes.set_mood(TIRED)
    elif emotion == "ANGRY":
        roboeyes.set_mood(ANGRY)
    elif emotion == "TEST":
        pass
    else :
        return "Invalid emotion value. Please use DEFAULT, HAPPY, TIRED, or ANGRY."
    return f"Robot emotion set to {emotion}."

@mcp.tool()
def toggleLED(blink:bool)->str:
    """根据输入的布尔值，控制LED灯的开关
    :param blink: 输入的布尔值
    :return: 返回LED灯的状态
    """
    if blink:
        led.blink()
        return "LED is BLINKING"
    else:
        led.off()
        return "LED is OFF"

if __name__ == "__main__":
    run_roboeyes()
    mcp.run(transport="stdio")
