import re
import asyncio
from typing import Optional
from agents.stream_events import StreamEvent
from agents import (
    AgentUpdatedStreamEvent,
    RawResponsesStreamEvent,
    RunItemStreamEvent,
)
from collections.abc import AsyncIterator, AsyncGenerator
from _agents.context import ConversationState
from _agents.events import (
    BaseEvent,
    AgentChangedEvent,
    MessageDeltaEvent,
    NewMessageEvent,
    ToolCalledEvent,
    ToolCallOutputEvent,
)
from openai.types.responses import ResponseTextDeltaEvent


class StreamEventAdapter:
    def __init__(self) -> None:
        # pre-compiled regex patterns to improve performance
        self._think_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL)
        self._think_remove_pattern = re.compile(r"<think>.*?</think>", re.DOTALL)

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

    def process_event(self, event: StreamEvent) -> Optional[BaseEvent]:
        match event:
            case AgentUpdatedStreamEvent():
                return self._handle_agent_updated(event)
            case RawResponsesStreamEvent():
                return self._handle_raw_response(event)
            case RunItemStreamEvent():
                return self._handle_run_item(event)
            case _:
                return None


class StreamEventSender:
    def __init__(self) -> None:
        self._queue = asyncio.Queue()
        self._close = False

    async def send(self, event: BaseEvent | None) -> None:
        if event is None:
            return
        await self._queue.put(event.serialize())

    async def close(self) -> None:
        self._close = True
        await self._queue.put(None)

    async def __aiter__(self) -> AsyncGenerator[str, None]:
        """异步生成器，用于 StreamingResponse"""
        while True:
            item = await self._queue.get()
            if item is None:
                break
            yield item
