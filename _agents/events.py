import time
from pydantic import BaseModel, Field
from typing import Dict, Any


class BaseEvent(BaseModel):
    timestamp: float = Field(default=time.time())

    def serialize(self) -> str:
        return self.model_dump_json() + "\n"


class AgentChangedEvent(BaseEvent):
    name: str = "AgentChangedEvent"
    current_agent: str


class MessageDeltaEvent(BaseEvent):
    name: str = "MessageDeltaEvent"
    delta: str


class NewMessageEvent(BaseEvent):
    name: str = "NewMessageEvent"
    content: str
    think: str | None
    agent: str


class ToolCalledEvent(BaseEvent):
    name: str = "ToolCalledEvent"
    tool_name: str
    tool_call_id: str
    args: str


class ToolCallOutputEvent(BaseEvent):
    name: str = "ToolCallOutputEvent"
    output: str
    call_id: str
