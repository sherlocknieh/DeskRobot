import subprocess
import threading
import os


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
binary_path = os.path.join(ROOT_DIR, "tools/SoundWireServer/SoundWireServer.bin")

process = None

def start_server():
    try:
        process = subprocess.Popen(
            [binary_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,  # 使用文本模式
            bufsize=1  # 行缓冲
        )
        print(f"服务已启动，进程 ID: {process.pid}")
    except PermissionError:
        print(f"错误：没有执行权限，请运行 'chmod +x {binary_path}'")
    except FileNotFoundError:
        print(f"错误：找不到文件 {binary_path}")


def stop_server():
    try:
        # 优先尝试优雅地终止进程
        if 'process' in globals() and process.poll() is None:
            process.terminate()
            print(f"正在停止服务 (PID: {process.pid})")
            # 给进程一些时间来清理
            process.wait(timeout=5)
        else:
            # 如果上面的方法失败，使用 killall
            subprocess.run(["killall", "SoundWireServer"])
        print("服务已停止")
    except subprocess.TimeoutExpired:
        # 如果进程没有及时响应 terminate，强制结束它
        process.kill()
        print("服务被强制终止")
    except Exception as e:
        print(f"停止服务时出错: {e}")


def io_loop():
    try:
        while True:
                command = input("请输入命令 (run/stop/exit): ")
                if command == "run":
                    start_server()
                elif command == "stop":
                    stop_server()
                elif command == "exit":
                    if 'process' in globals() and process.poll() is None:
                        stop_server()
                    break
                elif command:
                    print("命令错误！可用命令：run, stop, exit")
    except KeyboardInterrupt:
        print("\n正在退出程序...")
        if 'process' in globals() and process.poll() is None:
            stop_server()
    