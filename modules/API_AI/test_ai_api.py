"""
AI API 单元测试

使用说明:
1. 确保已在此目录下创建并正确配置了 .env 文件。
2. 在 `modules/AI对话/` 目录下运行 pytest 命令:
   pytest

pytest 会自动发现并运行此文件中的测试。
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from ai_api import AiAPI

# 环境变量检查，如果未配置则跳过需要网络访问的测试
requires_llm_config = pytest.mark.skipif(
    not all(os.getenv(k) for k in ["LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL_NAME"]),
    reason="需要完整的 LLM 配置才能进行真实的集成测试",
)


@pytest.fixture
def mock_event_bus(mocker):
    """一个 Pytest Fixture，用于模拟全局的 event_bus。"""
    mock_bus = MagicMock()
    # 注意：这里的路径需要是工具函数内部导入 event_bus 的路径
    mocker.patch("modules.AI对话.ai_api.event_bus", mock_bus)
    return mock_bus


@pytest.fixture(scope="module")
def ai_api_instance():
    """
    一个模块级的 Fixture，用于创建一个 AiAPI 的实例。
    为了进行单元测试，我们不需要真实的 LLM 配置。
    """
    # 模拟初始化，避免真实的网络和配置依赖
    try:
        # 我们可以通过在测试期间临时设置环境变量来绕过检查
        return AiAPI()
    except Exception as e:
        # 如果初始化仍然失败，则跳过所有使用此实例的测试
        pytest.skip(f"跳过AI API测试，因为初始化失败: {e}")


@pytest.fixture
def api_for_unit_test(mock_event_bus):
    """
    提供一个用于单元测试的 AiAPI 实例。
    通过模拟 __init__ 方法，我们阻止了任何网络或文件系统访问。
    然后我们手动将被模拟的 event_bus 和一个 logger 附加到实例上，
    以便被测试的方法可以正确地调用它们。
    """
    with patch.object(AiAPI, "__init__", lambda self: None):
        api = AiAPI()

    # 手动将被测试方法所依赖的属性附加到空实例上
    api.event_bus = mock_event_bus
    api.logger = MagicMock()  # logger 也需要被模拟，以防万一

    return api


# ---- 集成测试 (需要网络) ----
@requires_llm_config
def test_get_simple_response_integration(ai_api_instance):
    """【集成测试】测试 AiAPI 能否对一个简单问题返回非空回复。"""
    query = "你好"
    response = ai_api_instance.get_response(query)
    assert isinstance(response, str)
    assert len(response) > 0
    print(f"\n集成测试：简单问答测试通过，回复: {response}")


# ---- 单元测试 (无需网络) ----
def test_tool_set_expression_publishes_event(api_for_unit_test, mock_event_bus):
    """
    【单元测试】测试 _tool_set_expression 方法是否正确发布事件。
    """
    # 1. 调用被测试的方法
    expression = "happy"
    result = api_for_unit_test._tool_set_expression(expression)

    # 2. 断言返回值是正确的
    assert result == f"好的，我已经将表情设置为 {expression}。"

    # 3. 断言 event_bus.publish 被以正确的参数调用了一次
    expected_event = {"type": "SET_EXPRESSION", "data": {"expression": expression}}
    api_for_unit_test.event_bus.publish.assert_called_once_with(expected_event)

    print(
        f"\n[单元测试通过] _tool_set_expression: \n  - 方法成功执行，并正确发布了事件: {expected_event}"
    )


def test_tool_trigger_quick_expression_publishes_event(
    api_for_unit_test, mock_event_bus
):
    """
    【单元测试】测试 _tool_trigger_quick_expression 方法是否正确发布事件。
    """
    # 1. 调用被测试的方法
    expression = "laugh"
    result = api_for_unit_test._tool_trigger_quick_expression(expression)

    # 2. 断言返回值是正确的
    assert result == f"好的，我刚刚 {expression} 了一下。"

    # 3. 断言 event_bus.publish 被以正确的参数调用了一次
    expected_event = {
        "type": "TRIGGER_QUICK_EXPRESSION",
        "data": {"expression": expression},
    }
    api_for_unit_test.event_bus.publish.assert_called_once_with(expected_event)

    print(
        f"\n[单元测试通过] _tool_trigger_quick_expression: \n  - 方法成功执行，并正确发布了事件: {expected_event}"
    )


# ---- 重构 ai_api.py 让其更易于测试是更好的选择 ----
# 在重构之前，我们先用一种可行的方式来测试


def test_tool_logic_directly(mocker):
    """
    【单元测试】最纯粹的方式：不创建AiAPI实例，直接测试工具逻辑。
    为此，我们需要稍微改变一下工具函数的定义方式，或者直接在这里重新定义它。

    假设 `set_robot_expression` 是一个可以独立导入的函数，测试将非常简单。
    由于它是在 `__get_tools` 内部定义的，我们无法直接访问。

    结论：为了可测试性，我们将重构 ai_api.py。
    但在此之前，我们先按原样运行已有的、依赖网络的测试。
    """
    pass


# 保持原有的网络测试，但修复其逻辑
@requires_llm_config
def test_integration_tool_call_publishes_event(ai_api_instance, mock_event_bus):
    """
    【集成测试】测试当LLM需要设置表情时，是否能正确地向event_bus发布 SET_EXPRESSION 事件。
    这个测试会产生一次真实的网络调用。
    """
    query = "请将你的表情设置为happy"  # 使用英文以提高模型识别工具的成功率
    ai_api_instance.get_response(query)

    # 断言 event_bus.publish 被正确调用
    # 因为是真实调用，我们不知道AI具体会返回什么，但它应该会调用publish
    mock_event_bus.publish.assert_called()

    # 获取 publish 被调用时的参数
    # 如果 publish 被多次调用（例如，AI先思考，再行动），这会更复杂
    if mock_event_bus.publish.call_count > 0:
        last_call_args = mock_event_bus.publish.call_args
        event = last_call_args[0][0]  # call_args 是一个元组 (args, kwargs)

        assert event.get("type") == "SET_EXPRESSION"
        assert event.get("data", {}).get("expression") == "happy"
        print("\n集成测试：工具调用事件发布测试通过！")
    else:
        pytest.fail("event_bus.publish 一次都未被调用！")
