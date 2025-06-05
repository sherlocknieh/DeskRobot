from threading import Thread

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
    robot.add_task(lambda: print("Task 1"))
    robot.add_task(lambda: print("Task 2"))
    robot.run()
