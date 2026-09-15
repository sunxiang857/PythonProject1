from abc import ABC, abstractmethod
from typing import List
from internal.schema.message import ToolCall, ToolDefinition, ToolResult


class Registry(ABC):
    """工具注册中心抽象接口"""
    @abstractmethod
    def get_available_tools(self) -> List[ToolDefinition]:
        pass

    @abstractmethod
    def execute(self, call: ToolCall) -> ToolResult:
        pass