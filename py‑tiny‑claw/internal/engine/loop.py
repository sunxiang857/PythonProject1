from typing import List
from internal.provider.interface import LLMProvider
from internal.tools.registry import Registry
from internal.schema.message import Message, ROLE_SYSTEM, ROLE_USER


class AgentEngine:
    """ReAct真正心脏：MainLoop引擎，只依赖抽象接口，不绑定具体实现"""
    def __init__(self, provider: LLMProvider, registry: Registry, work_dir: str):
        self.provider = provider
        self.registry = registry
        self.work_dir = work_dir

    def run(self, user_prompt: str) -> None:
        # ========== 初始化上下文Context ==========
        context_history: List[Message] = [
            Message(
                role=ROLE_SYSTEM,
                content="You are py‑tiny‑claw, an expert coding assistant. You have full access to tools in the workspace."
            ),
            Message(
                role=ROLE_USER,
                content=user_prompt
            )
        ]

        turn_count = 0
        while True:
            turn_count += 1
            print(f"\n===== 🌀 Turn {turn_count} 开始 =====")

            # 获取本轮可用工具列表
            available_tools = self.registry.get_available_tools()

            # -------- Step1 Reason 推理阶段：调用Provider获取模型响应 --------
            try:
                response_msg = self.provider.generate(context_history, available_tools)
            except Exception as e:
                raise RuntimeError(f"模型生成失败: {e}") from e

            # 将assistant消息追加到上下文记忆
            context_history.append(response_msg)
            if response_msg.content:
                print(f"🧠模型思考：{response_msg.content}")

            # -------- 判断终止条件：没有tool_calls，任务结束 --------
            tool_calls = response_msg.tool_calls
            if (tool_calls is None) or (len(tool_calls) == 0):
                print("\n✅ 无工具调用，ReAct循环终止，最终回答：")
                print(response_msg.content)
                return

            # -------- Step2 Act行动阶段：执行全部工具调用 --------
            for one_call in tool_calls:
                print(f"🔧 执行工具调用 name={one_call.name}, args={one_call.arguments}")
                tool_result = self.registry.execute(one_call)

                # -------- Step3 Observe观察阶段：把工具结果包装成Message写回Context --------
                observe_msg = Message(
                    role=ROLE_USER,
                    content=tool_result.output,
                    tool_call_id=tool_result.tool_call_id
                )
                context_history.append(observe_msg)
                print(f"👁️观察(工具返回):\n{tool_result.output}")