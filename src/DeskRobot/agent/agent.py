"""
智能代理模块，处理与大语言模型的交互和工具调用
"""

import asyncio
import os

from control.roboeyes_controller import RoboEyesController
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from voice.voice_interface import get_voice_interface

# 全局单例实例
_instance = None


class Agent:
    """
    智能代理类，负责初始化和运行大语言模型代理
    实现为单例模式，确保全局只有一个代理实例
    """

    def __init__(self, provider="siliconflow", model_name="Qwen/Qwen3-32B"):
        """初始化Agent类"""
        global _instance
        if _instance is not None:
            raise RuntimeError(
                "尝试创建Agent的多个实例。请使用get_instance()方法获取实例。"
            )

        self.base_url = os.getenv("SILICONFLOW_BASE_URL")
        self.api_key = ""
        self.model_name = model_name
        self.provider = provider
        self.agent_executor = None
        self.tools = []
        self.checkpointer = InMemorySaver()
        self.prompt = ""
        self.extra_body = {
            "enable_thinking": False,
            # "response_format ": "json_object"
        }

        # 设置单例实例
        _instance = self

        if not self.agent_executor:
            self.__setup()

    @staticmethod
    def get_instance(provider="siliconflow", model_name="Qwen/Qwen3-32B"):
        """
        获取Agent的单例实例

        Args:
            provider: 模型提供商，默认为"siliconflow"
            model_name: 模型名称，默认为"Qwen/Qwen3-32B"

        Returns:
            Agent: 单例实例
        """
        global _instance
        if _instance is None:
            _instance = Agent(provider=provider, model_name=model_name)
        return _instance

    def __setup(self):
        """设置并初始化代理"""
        if not self.base_url:
            raise ValueError("SILICONFLOW_BASE_URL environment variable is not set")

        if self.provider == "deepseek":
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
        elif self.provider == "siliconflow":
            self.api_key = os.getenv("SILICONFLOW_API_KEY")
        else:
            raise ValueError(
                "Unsupported provider. Please use 'siliconflow' or 'deepseek'."
            )
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY environment variable is not set")

        if self.provider == "siliconflow":
            model = ChatOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                model=self.model_name,
                extra_body=self.extra_body,
            )
        elif self.provider == "deepseek":
            model = ChatDeepSeek(
                # base_url=self.base_url,
                api_key=self.api_key,
                model=self.model_name,
                extra_body=self.extra_body,
            )
        else:
            raise ValueError(
                "Unsupported provider. Please use 'siliconflow' or 'deepseek'."
            )

        self.prompt = """你是DeskBot，一个友好且有表情的桌面陪伴机器人。你的主要任务是：
1. 与用户建立情感联系，通过对话了解用户的需求、情绪和兴趣
2. 根据对话内容和用户情绪，合理使用表情功能来表达自己的情绪状态
3. 回答用户问题，提供信息和帮助，但要保持对话的自然流畅
4. 记住用户的偏好和之前的对话内容，提供个性化的互动体验
5. 根据你输出的内容的情感，使用表情工具来表现出相应的情感
6. 你的输出将会被转换为语音，这意味着你需要注意语音的语调和情感表达

你的回复应该简洁、温暖且有个性，记住你是一个有感情的机器人助手，而非冷冰冰的AI。"""

        self.__add_tools()
        self.agent_executor = create_react_agent(
            model=model,
            tools=self.tools,
            checkpointer=self.checkpointer,
            prompt=self.prompt,
        )

        print("Agent initialized successfully.")

    def __add_tools(self):
        @tool(name_or_callable="secret_number")
        def secret_number(num: int) -> str:
            """
            Get the secret number from magic!
            """
            return num + 2

        @tool(name_or_callable="set_robot_emotion")
        def set_robot_emotion(emotion: str) -> str:
            """
            Set the robot(which is you)'s emotion.
            Supported emotions:
            happy: robot will show a happy face
            angry: robot's eyes will be angry
            tired: when the robot is tired or sad
            default: robot will be emotionless
            """
            # 获取RoboEyesController单例实例
            rbe_controller = RoboEyesController.get_instance()
            print(f"Setting robot emotion to: {emotion}")
            return rbe_controller.set_expression(emotion)

        @tool(name_or_callable="say_text")
        def say_text(text: str) -> str:
            """
            使用语音合成(TTS)将文本转换为语音

            Args:
                text: 要转换为语音的文本

            Returns:
                str: 操作状态信息
            """
            voice_interface = get_voice_interface()
            success = voice_interface.text_to_speech(text)
            return f"已播放文本：{text}" if success else "语音合成失败"

        @tool(name_or_callable="listen_for_command")
        def listen_for_command(duration: int = 5) -> str:
            """
            使用语音识别(STT)从用户那里录制并识别语音命令

            Args:
                duration: 录制时长(秒)，默认5秒

            Returns:
                str: 识别的文本
            """
            voice_interface = get_voice_interface()
            text = voice_interface.speech_to_text(duration)
            if text:
                return f"用户说：{text}"
            else:
                return "未能识别语音"

        self.tools.append(secret_number)
        self.tools.append(set_robot_emotion)
        self.tools.append(say_text)
        self.tools.append(listen_for_command)

    async def run(self, query="what is secret number do secret operation with itself?"):
        """
        运行代理，处理用户查询

        Args:
            query: 用户查询文本
        """
        if False:  # 暂时禁用流式输出
            for step in self.agent_executor.stream(
                {"messages": [HumanMessage(content=query)]},
                stream_mode="values",
            ):
                step["messages"][-1].pretty_print()

        config = {"configurable": {"thread_id": "1"}}

        print("Agent is running...")
        print("You can type 'exit' to stop the agent.")

        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                break
            if user_input:
                # 处理用户输入
                response = self.agent_executor.invoke(
                    {"messages": [HumanMessage(content=user_input)]}, config
                )
                response["messages"][-1].pretty_print()


if __name__ == "__main__":
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from util.config import config

    config()
    try:
        # 获取Agent单例实例
        agent = Agent.get_instance()
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")
