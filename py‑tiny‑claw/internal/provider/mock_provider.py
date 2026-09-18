from typing import List, Optional
from internal.provider.interface import LLMProvider
from internal.schema.message import (
    Message, ToolDefinition, ToolCall,
    ROLE_ASSISTANT,
)


class MockLLMProvider(LLMProvider):
    """假大脑：Mock模拟大模型，已升级支持 Two-Stage ReAct 两阶段演练。

    升级要点（第 3 讲 慢思考）：
    - 发现 available_tools == None 时 => 处于 Phase 1 Thinking 阶段，
      假装在慢思考，输出一段纯文本推理与规划（不返回 ToolCall）；
    - 发现传入了工具时 => 才进入行动阶段，按轮次返回 ToolCall / 最终答案。
    """

    def __init__(self):
        # 只在行动阶段（有工具）递增，模拟不同轮次返回不同内容
        self._turn_counter = 0

    def generate(self,
                 messages: List[Message],
                 available_tools: Optional[List[ToolDefinition]]) -> Message:
        # 没有工具可用 => 处于 Thinking 阶段（小黑屋），只能输出纯文本思考
        if not available_tools:
            return Message(
                role=ROLE_ASSISTANT,
                content="【推理中】目标是检查文件。我不能直接盲猜，我需要先调用 bash 执行 ls 看看目录。",
            )

        # 恢复工具挂载 => 进入行动阶段
        self._turn_counter += 1
        turn = self._turn_counter

        if turn == 1:
            # 行动 Turn1：执行刚才计划的第一步，调用bash ls -la
            return Message(
                role=ROLE_ASSISTANT,
                content="我要执行我刚才计划的步骤了。",
                tool_calls=[
                    ToolCall(
                        id="call_123",
                        name="bash",
                        arguments='{"command": "ls -la"}'
                    )
                ]
            )
        elif turn == 2:
            # 行动 Turn2：看到ls返回，读取main.py检查代码
            return Message(
                role=ROLE_ASSISTANT,
                content="继续执行计划：目录里有main.py，读取它检查是否有bug。",
                tool_calls=[
                    ToolCall(
                        id="call_124",
                        name="read_file",
                        arguments='{"path": "main.py"}'
                    )
                ]
            )
        elif turn == 3:
            # 行动 Turn3：读取完毕，不再调用工具，输出最终答案，终止循环
            return Message(
                role=ROLE_ASSISTANT,
                content="根据工具返回结果，我看到了main.py，任务完成！",
                tool_calls=None
            )
        else:
            # 兜底终止
            return Message(
                role=ROLE_ASSISTANT,
                content="达到模拟最大轮次，任务结束。",
                tool_calls=None
            )
