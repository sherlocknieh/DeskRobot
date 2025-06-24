# 温湿度传感器
# pip install adafruit-circuitpython-dht

import adafruit_dht
import board
import time

dhtDevice = adafruit_dht.DHT11(board.D18) # DHT11传感器, 连接到GPIO18

while True:
    try:
        temperature_c = dhtDevice.temperature        # 温度
        humidity = dhtDevice.humidity                # 湿度
        print("Temp:  {:.1f} C    Humidity: {}% ".format(temperature_c, humidity))

    except RuntimeError as error:               # 读取数据出错
        print(error.args[0])                    # 打印错误信息
        time.sleep(2.0)                         # 等待2秒后继续
        continue                                # 跳过本次循环
    except Exception as error:                # 其他错误
        dhtDevice.exit()                      # 释放资源
        raise error                           # 抛出错误
    time.sleep(2.0)                # 2秒更新一次数据
