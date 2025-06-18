from threading import Thread
from modules.DataCenter import DataCenter
from modules.LED_Thread import LED_Control

class DeskRobot:
    def __init__(self):
        self.data = DataCenter()
        self.tasks = []

    def add(self, task):
        self.tasks.append(task)

    def start(self):
        print("DeskRobot is running")
        Thread(target=self._loop).start()
        for task in self.tasks:
            task.start(self.data)

    def stop(self):
        for task in self.tasks:
            task.stop()

    def _loop(self):
        while True:
            cmd = input("Enter command: ").strip()
            if cmd in ["exit", "quit", "stop"]:
                self.stop()
                break
            elif cmd == "led on":
                self.data.LED_status['status'] = "on"
            elif cmd == "led off":
                self.data.LED_status['status'] = "off"
            else: 
                print("Invalid command")

        print("DeskRobot is stopped")
        
if __name__ == "__main__":
    robot = DeskRobot()
    robot.add(LED_Control())
    robot.start()
