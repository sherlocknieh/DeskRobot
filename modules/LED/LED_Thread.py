if __name__ == '__main__':
    from LED_API import RGB
else:
    from .LED_API import RGB

class LED_Thread:
    def __init__(self):
        self.status = {'mode': 'off', 'r': 0, 'g': 0, 'b': 0,'speed': 1}
    def input_ouput(self):
        while True:
            key,value = input('Enter command: ').split()
            if not self.status.get(key) or value == self.status[key]:
                continue

            self.status[key] = value

            if key =='mode':
                if value == 'breeze':
                    Thread(target=self.breeze_loop).start()
                elif value == 'off':
                    self.red.off()
                    self.green.off()
                    self.blue.off()
                elif value == 'on':
                    self.red.on()
                    self.green.on()
                    self.blue.on()
                else:
                    print('unkown mode')
            elif key == 'r':
                self.red.value = float(value)
            elif key == 'g':
                self.green.value = float(value)
            elif key == 'b':
                self.blue.value = float(value)
            elif key =='speed':
                self.status['speed'] = int(value)
            else:
                print('unkown command')