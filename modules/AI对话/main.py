import asyncio
import threading
import time

from modules.AI对话.agent import Agent
from util.config import config


def main():
    config()
    try:


        agent = Agent.get_instance(provider="deepseek", model_name="deepseek-chat")
        def run_agent():
            asyncio.run(agent.run())

        agent_thread = threading.Thread(target=run_agent, name="Agent")

        # 设置为守护线程，这样主线程结束时它们会自动终止
        agent_thread.daemon = True

        # 启动线程
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
    main()
