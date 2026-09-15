from typing import List, Optional
from internal.provider.interface import LLMProvider
from internal.schema.message import Message, ToolDefinition, ToolCall


class MockLLMProvider(LLMProvider):
    """假大脑：Mock模拟大模型，硬编码模拟多轮ReAct输出"""
    def __init__(self):
        # 记录已经跑过多少轮turn，模拟不同轮次返回不同内容
        self._turn_counter = 0

    def generate(self,
                 messages: List[Message],
                 available_tools: Optional[List[ToolDefinition]]) -> Message:
        self._turn_counter += 1
        turn = self._turn_counter

        if turn == 1:
            # Turn1：模型思考，调用bash ls‑la
            return Message(
                role="assistant",
                content="让我先查看当前目录有哪些文件。",
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="bash",
                        arguments='{"command":"ls -la"}'
                    )
                ]
            )
        elif turn == 2:
            # Turn2：看到ls返回，调用read_file读取main.py
            return Message(
                role="assistant",
                content="看到目录下存在main.py，读取源码查看。",
                tool_calls=[
                    ToolCall(
                        id="call_002",
                        name="read_file",
                        arguments='{"path":"main.py"}'
                    )
                ]
            )
        elif turn ==3:
            # Turn3：读取完毕，不再调用工具，输出最终答案，终止循环
            return Message(
                role="assistant",
                content="main.py已经检查完毕，代码无语法错误，任务完成。",
                tool_calls=None
            )
        else:
            # 兜底终止
            return Message(
                role="assistant",
                content="达到模拟最大轮次，任务结束。",
                tool_calls=None
            )