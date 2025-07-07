"""
温湿度传感器模块
定时读取环境温湿度
当
"""

# 自定义模块
if __name__ != '__main__':
    from .EventBus import EventBus


# 第三方库
# pip install adafruit-circuitpython-dht
import adafruit_dht
import board
import time


# 标准库
import threading
import queue
import time


class Temperature(threading.Thread):
    def __init__(self, pin=board.D25):
        super().__init__(daemon=True, name="温湿度模块")
        self.dhtDevice = adafruit_dht.DHT11(pin) # DHT11传感器
        self.event_queue = queue.Queue()
        self.event_bus = EventBus()
        self.temperature = 0
        self.humidity = 0
        
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        self.event_bus.subscribe("GET_TEMPERATURE", self.event_queue, self.name)


    def run(self):
        threading.Thread(target=self.data_updater, daemon=True).start()
        while True:
            event = self.event_queue.get()
            if event['type'] == "EXIT":
                break
            elif event['type'] == "GET_TEMPERATURE":
                self.event_bus.publish("TEMPERATURE", {"temperature": self.temperature, "humidity": self.humidity})
        print("温湿度模块已退出")

    def data_updater(self):
        while True:
            try:
                self.temperature = self.dhtDevice.temperature
                self.humidity = self.dhtDevice.humidity
                if self.temperature is None: continue
                self.event_bus.publish(
                    "SUB_TEXT_STATIC_DISPLAY",
                    {
                        "text": f"温度: {self.temperature}",
                        "font_size": 16,
                        "position": (0, 0),
                        "duration" : 15
                    },
                    self.name
                )
                self.event_bus.publish(
                    "SUB_TEXT_STATIC_DISPLAY",
                    {
                        "text": f"湿度: {self.humidity}%",
                        "font_size": 16,
                        "position": (0, 16),
                        "duration" : 15
                    },
                    self.name
                )
                self.event_bus.publish(
                    "SPEAK_TEXT",
                    {
                        "text": f'当前温度 {self.temperature} 度，湿度 {self.humidity} %',
                    },
                    self.name
                )
            except:
                print("读取DHT11数据失败")
                continue
            time.sleep(60)

if __name__ == '__main__':

    from EventBus import EventBus

    temp = Temperature()
    temp.start()

    for i in range(5):
        print(f"Temperature: {temp.temperature} C, Humidity: {temp.humidity}%")
        temp.event_bus.publish("GET_TEMPERATURE")
        time.sleep(1)

    temp.event_bus.publish("EXIT")
