import logging
from typing import List
from internal.provider.interface import LLMProvider
from internal.tools.registry import Registry
from internal.schema.message import Message, ROLE_SYSTEM, ROLE_USER

log = logging.getLogger(__name__)


class AgentEngine:
    """Agent引擎：Two-Stage ReAct 两阶段慢思考循环

    把上一讲「一次请求带 tools 跑完思考与行动」的基础 Main Loop，
    升级为物理隔离的两阶段循环（机制决定行为）：

    Phase 1 · Thinking（慢思考）：
        不传 tools（传 None 剥夺工具），模型只能输出纯文本推理与规划，
        思考 Trace 追加进上下文，利用自回归引导后续行动。
    Phase 2 · Reason（带工具思考）：
        恢复 tools 列表，模型基于自己刚写下的规划生成 ToolCall。
    Phase 3 · Act + Observe：
        执行工具，把观察结果写回上下文，进入下一轮 Turn。
    """

    def __init__(self, provider: LLMProvider, registry: Registry, work_dir: str,
                 enable_thinking: bool = False):
        self.provider = provider
        self.registry = registry
        self.work_dir = work_dir
        # 慢思考开关：简单任务（如只问天气）可关闭，节省 Token；复杂代码任务则打开
        self.enable_thinking = enable_thinking

    def run(self, user_prompt: str) -> None:
        # ========== 初始化上下文Context ==========
        context_history: List[Message] = [
            Message(
                role=ROLE_SYSTEM,
                content="You are py-tiny-claw, an expert coding assistant. You have full access to tools in the workspace."
            ),
            Message(
                role=ROLE_USER,
                content=user_prompt
            )
        ]

        turn_count = 0
        while True:
            turn_count += 1
            print(f"\n========== [Turn {turn_count}] 开始 ==========")

            # 获取本轮可用工具列表
            available_tools = self.registry.get_available_tools()

            # ================= Phase 1: 慢思考 Thinking =================
            if self.enable_thinking:
                log.info("[Phase 1] 剥夺工具访问权，强制进入慢思考与规划阶段...")
                print("[Engine][Phase 1] 剥夺工具访问权，强制进入慢思考...")
                try:
                    # 核心魔法：第二个参数传 None，剥夺工具 Schema，
                    # 模型没有「诱饵」，只能乖乖输出纯文本推理与规划
                    think_resp = self.provider.generate(context_history, None)
                except Exception as e:
                    raise RuntimeError(f"Thinking 阶段失败: {e}") from e

                if think_resp.content != "":
                    print(f"[内部思考 Trace]: {think_resp.content}")
                # 把思考 Trace 追加进上下文（自回归：模型会顺着自己的计划行动）
                context_history.append(think_resp)
            else:
                print("[Engine] 慢思考模式: False，跳过 Phase 1 直接行动")

            # ================= Phase 2: Reason 思考（带工具） =================
            log.info("[Phase 2] 恢复工具挂载，等待模型行动...")
            print("[Engine][Phase 2] 恢复工具挂载，等待模型行动...")
            try:
                action_resp = self.provider.generate(context_history, available_tools)
            except Exception as e:
                raise RuntimeError(f"Action 阶段失败: {e}") from e
            context_history.append(action_resp)

            if action_resp.content != "":
                print(f"[对外回复]: {action_resp.content}")

            # ================= 执行判断 =================
            if not action_resp.tool_calls:  # None 或空列表都视为任务完成
                log.info("模型未请求工具，任务完成。")
                print("\n✅ [Engine] 模型未请求调用工具，任务宣告完成。")
                return

            print(f"[Engine] 模型请求调用 {len(action_resp.tool_calls)} 个工具...")

            # ================= Phase 3: Act + Observe 行动与观察 =================
            for tool_call in action_resp.tool_calls:
                print(f"-> 执行工具: {tool_call.name}, 参数: {tool_call.arguments}")
                result = self.registry.execute(tool_call)

                # 观察结果包装成 Message 写回 Context，进入下一轮
                observation_msg = Message(
                    role=ROLE_USER,
                    content=result.output,
                    tool_call_id=tool_call.id,
                )
                context_history.append(observation_msg)
                print(f"-> 工具执行成功 (返回 {len(result.output)} 字节)")
