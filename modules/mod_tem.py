"""
温湿度传感器模块

Subscribe:
- GET_TEMPERATURE: 请求获取温湿度数据
- STOP_THREADS: 停止线程

Publish:
- METER_DATA: 温湿度数据更新事件
    - payload格式:
    {
        "temperature": float,
        "humidity": float
    }
- ERROR: 传感器读取失败事件
"""

if __name__ == '__main__':
    from API_DHT.DHT import DHT11
    from EventBus import event_bus
else:
    from modules.API_DHT.DHT import DHT11
    from modules.EventBus import event_bus

import threading
import queue
import time

class TemperatureSensorThread(threading.Thread):
    def __init__(self, event_bus, gpio_pin=4):
        super().__init__(daemon=True, name="TemperatureSensorThread")
        self.event_bus = event_bus
        self.gpio_pin = gpio_pin  # 默认使用BCM编号的GPIO4
        self.sensor = DHT11(self.gpio_pin)
        self.event_queue = queue.Queue()
        self._stop_event = threading.Event()
        
        # 事件订阅
        self.event_bus.subscribe("GET_TEMPERATURE", self.event_queue, "温湿度模块")
        self.event_bus.subscribe("STOP_THREADS", self.event_queue, "温湿度模块")
        
        # 防止频繁读取的最小间隔（秒）
        self.min_interval = 2  
        self.last_read_time = 0

    def run(self):
        while not self._stop_event.is_set():
            try:
                event = self.event_queue.get(timeout=1)
                if event['type'] == "STOP_THREADS":
                    self.stop()
                    break
                elif event['type'] == "GET_TEMPERATURE":
                    self._read_sensor()
            except queue.Empty:
                pass

    def _read_sensor(self):
        # 确保读取间隔符合要求
        if time.time() - self.last_read_time < self.min_interval:
            return
            
        try:
            temperature, humidity = self.sensor.read()
            if temperature is not None and humidity is not None:
                self.event_bus.publish("METER_DATA", 
                    temperature=round(temperature, 1),
                    humidity=round(humidity, 1)
                )
            else:
                self.event_bus.publish("ERROR", message="传感器读取失败")
        except Exception as e:
            self.event_bus.publish("ERROR", message=f"传感器错误: {str(e)}")
        finally:
            self.last_read_time = time.time()

    def stop(self):
        self._stop_event.set()

if __name__ == '__main__':
    from mod_terminal_io import IOThread
    
    io_thread = IOThread(event_bus)
    sensor_thread = TemperatureSensorThread(event_bus)
    
    io_thread.start()
    sensor_thread.start()
    
    # 测试：手动发送获取数据请求
    event_bus.publish("GET_TEMPERATURE")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sensor_thread.stop()
        io_thread.stop()
