from internal.engine.loop import AgentEngine
from internal.provider.mock_provider import MockLLMProvider
from internal.tools.mock_registry import MockRegistry

def main():
    # 组装：假大脑(mock大模型) + 假手脚(mock工具) + 真心脏(ReAct主循环)
    mock_brain = MockLLMProvider()
    mock_hands = MockRegistry()
    engine = AgentEngine(
        provider=mock_brain,
        registry=mock_hands,
        work_dir="./demo_workspace"
    )

    user_query = "请检查当前目录main.py代码是否存在bug"
    print(f"📝 用户任务：{user_query}")
    engine.run(user_query)


if __name__ == "__main__":
    main()