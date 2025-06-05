import subprocess

binary_path = "data/SoundWireServer"

def start_server():
    process = subprocess.Popen([binary_path])
    # 获取输出和错误信息
    stdout, stderr = process.communicate()
    print("标准输出:", stdout.decode())
    print("错误输出:", stderr.decode())


def stop_server():
    process = subprocess.Popen(["killall", "SoundWireServer"])
    # 获取输出和错误信息
    stdout, stderr = process.communicate()
    print("标准输出:", stdout.decode())
    print("错误输出:", stderr.decode())

if __name__ == '__main__':
    while True:
        command = input("请输入命令：")
        if command == "start":
            start_server()
        elif command == "stop":
            stop_server()
        else:
            print("命令错误！")