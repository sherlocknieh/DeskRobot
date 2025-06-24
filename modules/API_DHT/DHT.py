from gpiozero import DigitalInputDevice, OutputDevice
import time

class DHT11:
    def __init__(self, pin):
        self.pin = pin
        self.max_retries = 20  # 最大重试次数
        self.timeout = 10000   # 超时微秒数

    def _read_bits(self, device):
        bits = []
        for _ in range(40):
            # 等待低电平开始
            loop_cnt = self.timeout
            while device.is_active:
                if loop_cnt <= 0:
                    raise TimeoutError("读取数据超时")
                loop_cnt -= 1
            
            # 测量高电平持续时间
            start = time.monotonic()
            loop_cnt = self.timeout
            while not device.is_active:
                if loop_cnt <= 0:
                    raise TimeoutError("读取数据超时")
                loop_cnt -= 1
            
            duration = time.monotonic() - start
            bits.append(0 if duration < 0.00005 else 1)  # 50微秒分界
        
        return bits

    def read(self):
        with OutputDevice(self.pin) as out:
            # 发送开始信号
            out.on()
            time.sleep(0.02)  # 保持高电平
            out.off()         # 拉低电平18ms以上
            time.sleep(0.02)
            
            # 切换为输入模式
            in_device = DigitalInputDevice(self.pin)
            
            # 等待传感器响应
            start = time.monotonic()
            while in_device.is_active:
                if time.monotonic() - start > 0.001:
                    raise TimeoutError("传感器无响应")

            # 读取40位数据
            bits = self._read_bits(in_device)
            
            # 解析数据
            data = [int(''.join(map(str, bits[i:i+8])), 2) 
                   for i in range(0, 40, 8)]
            
            # 校验和验证
            if sum(data[:4]) & 0xFF != data[4]:
                raise ValueError("校验和错误")
            
            # 转换温湿度值
            humidity = data[0] + data[1] * 0.1
            temperature = data[2] + data[3] * 0.1
            
            return temperature, humidity

        return None, None  # 仅在异常时返回
    
if __name__ == '__main__':
    # 传感器硬件测试代码
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    sensor = DHT11(4)
    while True:
        try:
            temp, humi = sensor.read()
            print(f"温度: {temp:.1f}℃, 湿度: {humi:.1f}%")
        except Exception as e:
            print(f"读取失败: {str(e)}")
        
        time.sleep(2)  # DHT11需要至少2秒间隔