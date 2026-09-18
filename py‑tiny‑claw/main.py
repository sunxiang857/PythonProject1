import logging

from internal.engine.loop import AgentEngine
from internal.provider.mock_provider import MockLLMProvider
from internal.tools.mock_registry import MockRegistry

# ========== 慢思考开关 ==========
# True  : Two-Stage ReAct，每轮先关进「小黑屋」强制慢思考（复杂任务推荐）
# False : 退回上一讲的基础 Main Loop，直接带工具行动（简单任务省 Token）
ENABLE_THINKING = True


def main():
    # 日志输出格式
    logging.basicConfig(
        level=logging.INFO,
        format="[Engine][LOG] %(message)s",
    )

    # 组装：假大脑(mock大模型) + 假手脚(mock工具) + 真心脏(Two-Stage ReAct主循环)
    mock_brain = MockLLMProvider()
    mock_hands = MockRegistry()
    engine = AgentEngine(
        provider=mock_brain,
        registry=mock_hands,
        work_dir="./demo_workspace",
        enable_thinking=ENABLE_THINKING,
    )

    user_query = "请检查当前目录main.py代码是否存在bug"
    print(f"📝 用户任务：{user_query}")
    print(f"🧠 慢思考模式 enable_thinking = {ENABLE_THINKING}")
    engine.run(user_query)


if __name__ == "__main__":
    main()
