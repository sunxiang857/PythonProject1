from typing import List
from internal.tools.registry import Registry
from internal.schema.message import ToolCall, ToolDefinition, ToolResult


class MockRegistry(Registry):
    """假手脚：Mock工具注册表，模拟bash/read_file，无真实IO"""
    def get_available_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="bash",
                description="执行终端shell命令",
                input_schema={
                    "type": "object",
                    "properties": {"command": {"type": "string"}}
                }
            ),
            ToolDefinition(
                name="read_file",
                description="读取指定路径文件",
                input_schema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}}
                }
            )
        ]

    def execute(self, call: ToolCall) -> ToolResult:
        """模拟工具执行，根据工具name返回伪造输出"""
        if call.name == "bash":
            fake_out = """total 12
drwxr-xr-x  2 user user 4096 Sep 14 10:00 .
drwxr-xr-x 10 user user 4096 Sep 14 09:00 ..
-rw-r--r--  1 user user  124 Sep 14 10:00 main.py
"""
            return ToolResult(tool_call_id=call.id, output=fake_out, is_error=False)
        elif call.name == "read_file":
            fake_code = """
def add(a,b):
    return a - b  # 这里有bug，加法写成减法
print(add(1,2))
"""
            return ToolResult(tool_call_id=call.id, output=fake_code, is_error=False)
        else:
            return ToolResult(
                tool_call_id=call.id,
                output=f"mock工具不支持:{call.name}",
                is_error=True
            )