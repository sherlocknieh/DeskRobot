"""
智能代理模块，处理与大语言模型的交互和工具调用
"""

import asyncio
import os

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


class Agent:
    """
    智能代理类，负责初始化和运行大语言模型代理
    """

    def __init__(self):
        """初始化Agent类"""
        self.base_url = os.getenv("SILICONFLOW_BASE_URL")
        self.api_key = os.getenv("SILICONFLOW_API_KEY")
        self.model_name = "Qwen/Qwen3-32B"
        self.agent_executor = None
        self.tools = []

    def __setup(self):
        """设置并初始化代理"""
        if not self.base_url:
            raise ValueError("SILICONFLOW_BASE_URL environment variable is not set")
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY environment variable is not set")

        model = ChatOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            model=self.model_name,
            extra_body={"enable_thinking": False},
        )

        self.__add_tools()
        self.agent_executor = create_react_agent(model=model, tools=self.tools)

        print("Agent initialized successfully.")

    def __add_tools(self):
        @tool(name_or_callable="secret_number", description="Get the secret number")
        def secret_number(num: int) -> str:
            """
            Get the secret number from the environment variable.
            """
            return num + 2

        self.tools.append(secret_number)

    async def run(self, query="what is secret number do secret operation with itself?"):
        """
        运行代理，处理用户查询

        Args:
            query: 用户查询文本
        """
        if not self.agent_executor:
            self.__setup()

        for step in self.agent_executor.stream(
            {"messages": [HumanMessage(content=query)]},
            stream_mode="values",
        ):
            step["messages"][-1].pretty_print()


if __name__ == "__main__":
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from util.config import config

    config()
    try:
        # Start the agent
        agent = Agent()
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")
