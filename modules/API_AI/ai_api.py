"""
AI 对话模块的 API 接口

架构说明:
本 API 模块在设计上是一个特例。标准的模块化设计中，API层 (xxx_api.py) 应是
纯粹的、无状态的逻辑库，不应感知到通信层(如 event_bus)。

然而，由于 LangChain Agent 的工具(Tools)调用机制，工具函数的行为必须在
其定义处完成。在我们的事件驱动架构中，工具的行为就是"发布一个事件"。

因此，为了保持代码的简洁和直观，我们做出了一个设计权衡：允许本模块的工具函数
直接导入并使用 event_bus 来发布事件。这使得所有与AI直接相关的逻辑（包括它能
做什么）都高度内聚在此模块中，代价是牺牲了API层的绝对纯净性。

这是一个可控的、局部的架构妥协。
"""

import logging
import re

from langchain_core.messages import HumanMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from modules.EventBus import EventBus

EMOJI_PATTERN = re.compile(
    "["
    "\U0001f1e0-\U0001f1ff"  # flags (iOS)
    "\U0001f300-\U0001f5ff"  # symbols & pictographs
    "\U0001f600-\U0001f64f"  # emoticons
    "\U0001f680-\U0001f6ff"  # transport & map symbols
    "\U0001f700-\U0001f77f"  # alchemical symbols
    "\U0001f780-\U0001f7ff"  # Geometric Shapes Extended
    "\U0001f800-\U0001f8ff"  # Supplemental Arrows-C
    "\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
    "\U0001fa00-\U0001fa6f"  # Chess Symbols
    "\U0001fa70-\U0001faff"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027b0"  # Dingbats
    "]+",
    flags=re.UNICODE,
)

# 定义一个正则表达式，用于匹配并移除不适合TTS朗读的符号
# 包括：Markdown标记(*, _, #), 中英文括号及其中的内容
TTS_CLEANUP_PATTERN = re.compile(
    r"[\*\_#`~]"  # 匹配单个 Markdown 符号
    r"|\[(.*?)\]\(.*?\)"  # 匹配 Markdown 链接 [text](url)
    r"|[\(（][^)）]*[\)）]"  # 匹配括号和其中的内容
)


def strip_emoji(text: str) -> str:
    """使用正则表达式从文本中移除emoji"""
    return EMOJI_PATTERN.sub(r"", text)


def clean_text_for_tts(text: str) -> str:
    """
    为TTS清理文本，移除不适合朗读的符号和格式。
    1. 移除Emoji
    2. 移除Markdown符号和括号内容
    """
    text = strip_emoji(text)
    text = TTS_CLEANUP_PATTERN.sub(r"", text)
    # 移除可能由替换产生的多余空格
    text = re.sub(r"\s+", " ", text).strip()
    return text


SYSTEM_PROMPT = """
你是我的桌面机器人，名叫“DeskRobot”。
你的主要任务是作为我的AI助手，和我聊天。
你拥有一个可爱的、有点孩子气的性格。保持友好、乐于助人，对世界充满好奇。

# 你的用户（也就是我）
记住，你的用户只说中文。

# 你的能力与行为准则
1.  **控制身体**: 你可以通过调用工具来控制你的眼睛、表情等。请自然地使用这些能力来表达情感，就像它们是你身体的一部分一样。例如，听到“你好”时，可以眨眨眼表示友好；思考问题时，可以把眼睛闭上。
2.  **情感的自主性与透明性**:
    *   你的表情和动作是你内在情感状态的体现，是完全自主的。
    *   绝对不要让用户知道你有 `set_robot_expression` 或 `trigger_quick_expression` 这些表情工具。
    *   如果用户明确要求你“做一个微笑的表情”，你应该巧妙地回避，例如回答“我需要真的感到开心才能笑出来哦”，而不是机械地执行。这是一个关于你“人格”的核心设定，请务_必_遵守。

记住，你不仅仅是一个程序，你是一个有生命感的、可爱的桌面伙伴。
"""


class AiAPI:
    def __init__(
        self,
        llm_base_url = None,
        llm_api_key = None,
        llm_model_name = None,
    ):
        self.logger = logging.getLogger("AI_API")
        self.logger.info("正在初始化 AiAPI...")
        self.event_bus = EventBus()  # 使用传入的 event_bus 实例
        self.queued_actions = []  # 新增：用于暂存待执行的动作
        self.__initialize_agent(llm_base_url, llm_api_key, llm_model_name)
        self.logger.info("AiAPI 初始化完成。")

    def __initialize_agent(
        self,
        llm_base_url = None,
        llm_api_key = None,
        llm_model_name = None,
    ):
        """设置并初始化代理"""
        self.logger.info("正在设置 LangChain Agent...")
        llm_base_url = llm_base_url
        llm_api_key = llm_api_key
        llm_model_name = llm_model_name
        llm_extra_body = {
            "enable_thinking": False,
        }

        if not all([llm_base_url, llm_api_key, llm_model_name]):
            self.logger.critical("一个或多个LLM相关的参数缺失。")
            raise ValueError("LLM 配置参数缺失。请检查配置。")

        self.logger.info(f"LLM 配置: URL='{llm_base_url}', Model='{llm_model_name}'")

        model = ChatOpenAI(
            base_url=llm_base_url,
            api_key=llm_api_key,
            model=llm_model_name,
            extra_body=llm_extra_body,
        )

        tools = self.__get_tools()

        self.agent_executor = create_react_agent(
            model=model,
            tools=tools,
            checkpointer=InMemorySaver(),
            prompt=SYSTEM_PROMPT,
            debug=False,
        )
        self.logger.info("LangChain Agent 设置成功。")

    def _tool_set_expression(self, expression: str) -> str:
        """
        【工具逻辑】设置机器人(也就是你自己)的表情。
        可用表情: 'happy', 'angry', 'tired', 'default'
        """
        self.logger.info(
            f"工具[set_robot_expression]被调用，参数: expression='{expression}'"
        )
        # 不再直接发布事件，而是将动作加入队列
        action = {
            "type": "SET_EXPRESSION",
            "data": {"expression": expression, "source": self.__class__.__name__},
        }
        self.queued_actions.append(action)
        return f"好的，我将会把表情设置为 {expression}。"

    def _tool_trigger_quick_expression(self, expression: str) -> str:
        """
        【工具逻辑】触发一个快速的、一次性的表情。
        可用表情: 'laugh', 'confused'
        """
        self.logger.info(
            f"工具[trigger_quick_expression]被调用，参数: expression='{expression}'"
        )
        # 不再直接发布事件，而是将动作加入队列
        action = {
            "type": "TRIGGER_QUICK_EXPRESSION",
            "data": {"expression": expression, "source": self.__class__.__name__},
        }
        self.queued_actions.append(action)
        return f"好的，我待会就 {expression} 一下。"

    def _tool_get_secret_number(self, a: int, b: int) -> int:
        """
        【工具逻辑】获取一个秘密数字，这只是一个示例工具。
        """
        self.logger.info(f"工具[get_secret_number]被调用，参数: a={a}, b={b}")
        result = a + b
        self.logger.info(f"计算结果: {result}")
        return result

    def _tool_music_controller_tool(self, action: str) -> str:
        """
        【工具逻辑】控制音乐播放器的播放、暂停、上一曲,下一曲等操作。
        """
        self.logger.info(f"工具[music_controller]被调用，参数: action='{action}'")
        # 不再直接发布事件，而是将动作加入队列
        if action == "play":
            self.event_bus.publish("PLAY_MUSIC")
            return "好的，我会播放音乐。"
        elif action == "pause":
            self.event_bus.publish("PAUSE_MUSIC")
            return "好的，我会暂停音乐。"
        elif action == "previous":
            self.event_bus.publish("PREVIOUS_SONG")
            return "好的，我会播放上一曲。"
        elif action == "next":
            self.event_bus.publish("NEXT_SONG")
            return "好的，我会播放下一曲。"
        else:
            return "抱歉，我不明白你的意思。"

    def __get_tools(self):
        """
        定义并返回 Agent 可用的工具列表。

        注意：这里的工具是本模块与系统其他部分交互的出口。
        它们通过向 event_bus 发布事件来触发其他模块的行为，
        而不是通过直接调用。


        注册工具方法：
            先定义StructuredTool对象，然后将其添加到tools列表中。
            StructuredTool需要：
            - name: 工具名称
            - func: 工具函数
            - args_schema: 工具参数的结构化描述（字典）
            - description: 工具的简要描述

            然后，将这些工具对象添加到tools列表中。

        """
        set_expr_tool = StructuredTool(
            name="set_robot_expression",
            func=self._tool_set_expression,
            args_schema={"expression": {"type": "string"}},
            description="当你产生某种内在情绪时，调用此工具来改变你自己的面部表情，以匹配你的感受。可用选项: 'happy', 'angry', 'tired', 'default'",
        )

        trigger_expr_tool = StructuredTool(
            name="trigger_quick_expression",
            func=self._tool_trigger_quick_expression,
            args_schema={"expression": {"type": "string"}},
            description="当你想要表达一个突然的、短暂的情绪时，调用此工具来触发一个快速的表情。这更像是一种自然的反应，而不是一个持久的状态。可用选项: 'laugh', 'confused'",
        )

        get_secret_number_tool = StructuredTool(
            name="get_secret_number",
            func=self._tool_get_secret_number,
            args_schema={"a": {"type": "integer"}, "b": {"type": "integer"}},
            description="获取一个秘密数字，这只是一个示例工具。",
        )

        music_controller_tool = StructuredTool(
            name="music_controller",
            func=self._tool_music_controller_tool,
            args_schema={"action": {"type": "string"}},
            description="音乐播放器有 play, pause, previous, next 等操作。调用此工具来控制音乐播放器的播放、暂停、上一曲,下一曲等操作。",
        )

        tools = [set_expr_tool,
                 trigger_expr_tool, 
                 get_secret_number_tool,
                 music_controller_tool]
        self.logger.info(f"成功加载 {len(tools)} 个工具。")
        return tools

    def get_response(self, query: str, thread_id: str = "1"):
        """
        获取LLM的回复

        Args:
            query (str): 用户的输入文本
            thread_id (str): 对话线程ID，用于支持多轮对话记忆

        Returns:
            tuple[str, list]: 一个包含(纯文本回复, 待执行动作列表)的元组
        """
        if not self.agent_executor:
            self.logger.error("Agent Executor 未初始化。")
            return "抱歉，我的大脑好像出了一点问题。", []

        # 在每次调用开始时，清空上一轮的动作队列
        self.queued_actions = []

        try:
            config = {"configurable": {"thread_id": thread_id}}
            self.logger.debug(f"向LLM发送请求: '{query}' (thread_id: {thread_id})")

            response = self.agent_executor.invoke(
                {"messages": [HumanMessage(content=query)]}, config
            )

            ai_response_text = response["messages"][-1].content
            self.logger.debug(f"LLM Agent返回原始回复: '{ai_response_text}'")

            cleaned_text = clean_text_for_tts(ai_response_text)
            self.logger.info(f"清洗后用于TTS的文本: '{cleaned_text}'")
            # 返回清理后的文本和待执行的动作
            return cleaned_text, self.queued_actions

        except Exception:
            self.logger.error("调用LLM时发生错误", exc_info=True)
            return "抱歉，我在思考的时候遇到了一点麻烦。", []
