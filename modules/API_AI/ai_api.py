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
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from modules.API_EventBus import event_bus
from utils.config import config

logger = logging.getLogger(__name__)

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


def strip_emoji(text: str) -> str:
    """使用正则表达式从文本中移除emoji"""
    return EMOJI_PATTERN.sub(r"", text)


class AiAPI:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("正在初始化 AiAPI...")
        self.event_bus = event_bus  # 依赖注入点
        self.__initialize_agent()
        self.logger.info("AiAPI 初始化完成。")

    def __initialize_agent(self):
        """设置并初始化代理"""
        self.logger.info("正在设置 LangChain Agent...")
        llm_base_url = config.get("LLM_BASE_URL")
        llm_api_key = config.get("LLM_API_KEY")
        llm_model_name = config.get("LLM_MODEL_NAME")
        llm_extra_body = {
            "enable_thinking": False,
        }

        if not all([llm_base_url, llm_api_key, llm_model_name]):
            self.logger.critical("一个或多个LLM相关的环境变量未设置。")
            raise ValueError("LLM 配置环境变量缺失，请检查 .env 文件。")

        self.logger.info(f"LLM 配置: URL='{llm_base_url}', Model='{llm_model_name}'")

        model = ChatOpenAI(
            base_url=llm_base_url,
            api_key=llm_api_key,
            model=llm_model_name,
            extra_body=llm_extra_body,
        )

        tools = self.__get_tools()

        # 优化后的系统提示词
        system_prompt = """你是一个名叫 DeskBot 的桌面陪伴机器人。你的回答总是友好、温暖且有个性。
你的主要任务是:
1.  与用户进行自然流畅的对话。
2.  根据对话内容和用户情绪，使用工具来设置你自己的表情，以实现情感化的互动。
"""

        self.agent_executor = create_react_agent(
            model=model,
            tools=tools,
            checkpointer=InMemorySaver(),
            prompt=system_prompt,
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
        self.event_bus.publish(
            "SET_EXPRESSION", source=self.__class__.__name__, expression=expression
        )
        return f"好的，我已经将表情设置为 {expression}。"

    def _tool_trigger_quick_expression(self, expression: str) -> str:
        """
        【工具逻辑】触发一个快速的、一次性的表情。
        可用表情: 'laugh', 'confused'
        """
        self.logger.info(
            f"工具[trigger_quick_expression]被调用，参数: expression='{expression}'"
        )
        self.event_bus.publish(
            "TRIGGER_QUICK_EXPRESSION",
            source=self.__class__.__name__,
            expression=expression,
        )
        return f"好的，我刚刚 {expression} 了一下。"

    def __get_tools(self):
        """
        定义并返回 Agent 可用的工具列表。

        注意：这里的工具是本模块与系统其他部分交互的出口。
        它们通过向 event_bus 发布事件来触发其他模块的行为，
        而不是通过直接调用。
        """
        set_expr_tool = Tool(
            name="set_robot_expression",
            func=self._tool_set_expression,
            description="设置机器人(也就是你自己)的表情。可用表情: 'happy', 'angry', 'tired', 'default'",
        )

        trigger_expr_tool = Tool(
            name="trigger_quick_expression",
            func=self._tool_trigger_quick_expression,
            description="触发一个快速的、一次性的表情。可用表情: 'laugh', 'confused'",
        )

        tools = [set_expr_tool, trigger_expr_tool]
        self.logger.info(f"成功加载 {len(tools)} 个工具。")
        return tools

    def get_response(self, query: str, thread_id: str = "1"):
        """
        获取LLM的回复

        Args:
            query (str): 用户的输入文本
            thread_id (str): 对话线程ID，用于支持多轮对话记忆

        Returns:
            str: 清理掉emoji后的纯文本回复
        """
        if not self.agent_executor:
            self.logger.error("Agent Executor 未初始化。")
            return "抱歉，我的大脑好像出了一点问题。"

        try:
            config = {"configurable": {"thread_id": thread_id}}
            self.logger.debug(f"向LLM发送请求: '{query}' (thread_id: {thread_id})")

            response = self.agent_executor.invoke(
                {"messages": [HumanMessage(content=query)]}, config
            )

            ai_response_text = response["messages"][-1].content
            self.logger.debug(f"LLM Agent返回原始回复: '{ai_response_text}'")

            cleaned_text = strip_emoji(ai_response_text)
            self.logger.info(f"清洗后用于TTS的文本: '{cleaned_text}'")
            return cleaned_text

        except Exception:
            self.logger.error("调用LLM时发生错误", exc_info=True)
            return "抱歉，我在思考的时候遇到了一点麻烦。"
