from abc import ABC, abstractmethod
from typing import List, Optional
from internal.schema.message import Message, ToolDefinition


class LLMProvider(ABC):
    """与大模型通信统一抽象接口"""
    @abstractmethod
    def generate(self,
                 messages: List[Message],
                 available_tools: Optional[List[ToolDefinition]]) -> Message:
        pass