import asyncio
import threading
import time

from agent import Agent
from control.roboeyes_controller import RoboEyesController
from util.config import config
from voice.piper_tts import get_piper_tts
from voice.voice_interface import get_voice_interface


def piper_test():
    # Initialize the TTS engine
    tts = get_piper_tts()

    # Define the text to be spoken
    text = "你好，我是桌面机器人。今天我能为你做些什么？"

    # Speak the text
    audio_path = tts.text_to_speech(text)
    print(f"Audio saved to: {audio_path}")


def remote_audio_test():
    config()
    # Initialize the voice interface
    voice = get_voice_interface()

    # Define the text to be spoken
    text = "你好，我是桌面机器人。今天我能为你做些什么？"

    # Speak the text
    audio_path = voice.text_to_speech(text)
    print(f"Audio saved to: {audio_path}")

    # Recognize speech
    recognized_text = voice.speech_to_text(5, save_audio=False)
    print(f"Recognized text: {recognized_text}")


def main():
    config()
    try:
        # 获取控制器和代理单例实例
        rbe_controller = RoboEyesController.get_instance()
        agent = Agent.get_instance(provider="deepseek", model_name="deepseek-chat")

        # 创建适配器函数来在线程中运行异步函数
        def run_rbe_controller():
            asyncio.run(rbe_controller.run())

        def run_agent():
            asyncio.run(agent.run())

        # 创建两个线程
        rbe_thread = threading.Thread(target=run_rbe_controller, name="RoboEyes")
        agent_thread = threading.Thread(target=run_agent, name="Agent")

        # 设置为守护线程，这样主线程结束时它们会自动终止
        rbe_thread.daemon = True
        agent_thread.daemon = True

        # 启动线程
        print("Starting RoboEyes controller...")
        rbe_thread.start()

        print("Starting Agent...")
        agent_thread.start()

        # 主线程等待，这里可以添加其他逻辑
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n接收到中断信号，正在退出...")
        return

    except Exception as e:
        print(f"错误: {e}")
        return


if __name__ == "__main__":
    # main()
    # piper_test()
    remote_audio_test()
