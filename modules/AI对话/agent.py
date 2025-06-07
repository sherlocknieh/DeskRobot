"""
智能代理模块，处理与大语言模型的交互和工具调用
"""


from control.roboeyes_controller import RoboEyesController
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from voice.voice_interface import get_voice_interface

import asyncio
import os

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
        
        @tool(name_or_callable="trigger_quick_expression")
        def trigger_quick_expression(expression: str) -> str:
            """ 
            触发快速表情(快速表情是指短暂的表情)
            Args:
                expression: 'laugh','confused'
                其中，laugh是短笑，具体表现为眼睛快速上下摆动，可以组合普通表情达到不同的效果，通常会增强普通表情的效果：比如angry+laugh=不怀好意的笑/坏笑/更加生气，happy+laugh=开心的笑/非常开心，tired+laugh=大哭，default+laugh=冷笑
                confused是困惑，具体表现为眼睛快速左右摆动，有种动摇的感觉，可以组合普通表情达到不同的效果
            """
            rbe_controller = RoboEyesController.get_instance()
            print(f"Triggering quick expression: {expression}")
            return rbe_controller.trigger_quick_expression(expression)

        self.tools.append(secret_number)
        self.tools.append(set_robot_emotion)
        self.tools.append(trigger_quick_expression)
    async def run(self, query="what is secret number do secret operation with itself?"):
        """
        运行代理，处理用户查询

        Args:
            query: 用户查询文本
        """
        config = {"configurable": {"thread_id": "1"}}

        print("Agent is running...")
        print("You can type 'exit' to stop the agent.")
        voice_interact = False
        if voice_interact:
            voice_interface = get_voice_interface()
            while True:
                user_input = voice_interface.speech_to_text(5, save_audio=True)
                if user_input:
                    # 处理用户输入
                    response = self.agent_executor.invoke(
                        {"messages": [HumanMessage(content=user_input)]}, config
                    )
                    response["messages"][-1].pretty_print()
                    # 语音合成
                    voice_interface.text_to_speech(response["messages"][-1].content)
        else:
            while True:
                user_input = input("You: ")
                if user_input.lower() == "exit":  # 退出循环
                    break
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
