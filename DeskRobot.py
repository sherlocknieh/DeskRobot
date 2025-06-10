from threading import Thread
from modules.LED.LED_Thread import LED_Control

class DeskRobot:
    def __init__(self):
        self.name = "DeskRobot"
        self.status = "idle"
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def run(self):
        print("DeskRobot is running")
        for task in self.tasks:
            Thread(target=task).start()


if __name__ == "__main__":
    robot = DeskRobot()
    #robot.add_task(LED_Thread.)
    robot.run()
