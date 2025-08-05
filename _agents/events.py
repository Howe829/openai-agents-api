import time
from pydantic import BaseModel, Field
from enum import Enum


class EventName(str, Enum):
    AGENT_CHANGED_EVENT = "AgentChangedEvent"
    MESSAGE_DELTA_EVENT = "MessageDeltaEvent"
    NEW_MESSAGE_EVENT = "NewMessageEvent"
    TOOL_CALLED_EVENT = "ToolCalledEvent"
    TOOL_CALL_OUTPUT_EVENT = "ToolCallOutputEvent"


class BaseEvent(BaseModel):
    timestamp: float = Field(default=time.time())

    def serialize(self) -> str:
        return self.model_dump_json() + "\n"


class AgentChangedEvent(BaseEvent):
    name: EventName = EventName.AGENT_CHANGED_EVENT
    current_agent: str


class MessageDeltaEvent(BaseEvent):
    name: EventName = EventName.MESSAGE_DELTA_EVENT
    delta: str


class NewMessageEvent(BaseEvent):
    name: EventName = EventName.NEW_MESSAGE_EVENT
    content: str
    think: str | None
    agent: str


class ToolCalledEvent(BaseEvent):
    name: EventName = EventName.TOOL_CALLED_EVENT
    tool_name: str
    tool_call_id: str
    args: str


class ToolCallOutputEvent(BaseEvent):
    name: EventName = EventName.TOOL_CALL_OUTPUT_EVENT
    output: str
    call_id: str
