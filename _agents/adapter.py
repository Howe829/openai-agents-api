import re
from dataclasses import dataclass
from typing import Optional, Callable
from agents.stream_events import StreamEvent
from agents import (
    AgentUpdatedStreamEvent,
    RawResponsesStreamEvent,
    RunItemStreamEvent,
)
from collections.abc import AsyncIterator
from _agents.events import (
    BaseEvent,
    AgentChangedEvent,
    MessageDeltaEvent,
    NewMessageEvent,
    ToolCalledEvent,
    ToolCallOutputEvent,
    EventName,
)
from openai.types.responses import ResponseTextDeltaEvent


@dataclass
class StreamEventAdapter:
    event_iterator: AsyncIterator
    handlers: dict[EventName, Callable]

    def __init__(self, event_interator: AsyncIterator) -> None:
        self.event_iterator = event_interator
        self.handlers = {}
        # pre-compiled regex patterns to improve performance
        self._think_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL)
        self._think_remove_pattern = re.compile(r"<think>.*?</think>", re.DOTALL)

    def register_handler(self, event_name: EventName, handler: Callable) -> None:
        self.handlers[event_name] = handler

    def _handle_agent_updated(
        self, event: AgentUpdatedStreamEvent
    ) -> Optional[BaseEvent]:
        return AgentChangedEvent(current_agent=event.new_agent.name)

    def _handle_raw_response(
        self, event: RawResponsesStreamEvent
    ) -> Optional[BaseEvent]:
        if not isinstance(event.data, ResponseTextDeltaEvent):
            return None
        return MessageDeltaEvent(delta=event.data.delta)

    def _handle_run_item(self, event: RunItemStreamEvent) -> Optional[BaseEvent]:
        match event.name:
            case "handoff_occured":
                return AgentChangedEvent(current_agent=event.item.target_agent.name)
            case "message_output_created":
                content = event.item.raw_item.content[0].text
                # 使用预编译的正则表达式提高性能
                cleaned_text = self._think_remove_pattern.sub("", content)
                think_match = self._think_pattern.search(content)
                think = think_match.group(1) if think_match else None
                return NewMessageEvent(
                    content=cleaned_text,
                    think=think,
                    agent=event.item.agent.name,
                )
            case "tool_called":
                return ToolCalledEvent(
                    args=event.item.raw_item.arguments,
                    tool_name=event.item.raw_item.name,
                    tool_call_id=event.item.raw_item.call_id,
                )
            case "tool_output":
                return ToolCallOutputEvent(
                    output=event.item.raw_item.get("output"),
                    call_id=event.item.raw_item.get("call_id"),
                )
            case _:
                return None

    def handle_event(self, event: Optional[BaseEvent]):
        if event is None:
            return
        handler = self.handlers.get(event.name)
        if handler is None:
            return
        handler(event)

    def process_event(self, event: StreamEvent) -> Optional[BaseEvent]:
        processed_event = None
        match event:
            case AgentUpdatedStreamEvent():
                processed_event = self._handle_agent_updated(event)
            case RawResponsesStreamEvent():
                processed_event = self._handle_raw_response(event)
            case RunItemStreamEvent():
                processed_event = self._handle_run_item(event)
        self.handle_event(processed_event)
        return processed_event

    async def stream_events(self):
        async for event in self.event_iterator:
            processed_event = self.process_event(event)
            if processed_event is None:
                continue
            yield processed_event.serialize()
