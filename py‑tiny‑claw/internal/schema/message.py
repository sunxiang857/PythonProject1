from dataclasses import dataclass
from typing import List, Optional, Dict, Any

# 角色常量
ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"


@dataclass
class ToolCall:
    """模型发起的一次工具调用请求"""
    id: str = ""
    name: str = ""
    arguments: str = ""


@dataclass
class ToolResult:
    """一次工具执行的结果"""
    tool_call_id: str = ""
    output: str = ""
    is_error: bool = False


@dataclass
class ToolDefinition:
    """暴露给模型的工具定义说明书"""
    name: str = ""
    description: str = ""
    input_schema: Optional[Dict[str, Any]] = None


@dataclass
class Message:
    """上下文流转的基本单元"""
    role: str = ""
    content: str = ""
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: str = ""