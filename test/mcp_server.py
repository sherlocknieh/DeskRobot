from mcp.server.fastmcp import FastMCP
from gpiozero import RGBLED

mcp = FastMCP("testServer")
led = RGBLED(2,3,4)


@mcp.tool()
def getSecretNumber(number: int) -> int:
    """根据输入数字，返回一个秘密数字
    :param number: 输入的数字
    :return: 返回一个秘密数字
    """
    return number + 10


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
    mcp.run(transport="stdio")
