import copy

from threading import Thread
if __name__ == '__main__':
    from LED.LED_API import RGB
else:
    from .LED.LED_API import RGB


class LED_Control:
    def __init__(self):
        self.rgb = RGB(10, 9, 11)
        self.task_name = 'LED'
        self.task_thread = None
        self.task_running = False

        self.current_status = None
        self.last_status = {
            "status": "off",
            "r" : 0,
            "g" : 0,
            "b" : 0,
            "speed": 1,
        }

    def start(self, data_center):
        self.current_status = data_center.LED_status
        self.task_thread = Thread(target=self._loop)
        self.task_running = True
        self.task_thread.start()

    def stop(self):
        self.task_running = False
        self.task_thread.join()
        print(f'Task {self.task_name} Stopped')

    def _loop(self):
        while self.task_running:
            if self.current_status!= self.last_status:
                self.last_status = copy.deepcopy(self.current_status)

                if self.last_status['status'] == 'on':
                    self.rgb.on(r=self.current_status['r'], g=self.current_status['g'], b=self.current_status['b'])
                elif self.current_status['status'] == 'off':
                    self.rgb.off()
                elif self.current_status['status'] == 'flash':
                    self.rgb.flash(speed=self.current_status['speed'])
                elif self.current_status['status'] == 'breeze':
                    self.rgb.breeze(speed=self.current_status['speed'])
                elif self.current_status['status'] == 'exit':
                    self.stop()
                else:
                    print(f'Invalid LED status: {self.current_status["status"]}')

           
    