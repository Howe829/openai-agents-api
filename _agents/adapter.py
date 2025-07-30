import re
from typing import Optional
from agents.stream_events import StreamEvent
from agents import (
    AgentUpdatedStreamEvent,
    RawResponsesStreamEvent,
    RunItemStreamEvent,
)
from collections.abc import AsyncIterator
from _agents.context import ConversationState
from _agents.events import (
    AgentChangedEvent,
    MessageDeltaEvent,
    NewMessageEvent,
    ToolCalledEvent,
    ToolCallOutputEvent,
)
from openai.types.responses import ResponseTextDeltaEvent


class StreamEventAdapter:
    def __init__(
        self, iterator: AsyncIterator[StreamEvent], state: ConversationState
    ) -> None:
        self.iterator = iterator
        self.state = state
        # pre-compiled regex patterns to improve performance
        self._think_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL)
        self._think_remove_pattern = re.compile(r"<think>.*?</think>", re.DOTALL)

    def _handle_agent_updated(self, event: AgentUpdatedStreamEvent) -> Optional[str]:
        if event.new_agent.name == self.state.current_agent:
            return None
        self.state.current_agent = event.new_agent.name
        return AgentChangedEvent(current_agent=event.new_agent.name).serialize()

    def _handle_raw_response(self, event: RawResponsesStreamEvent) -> Optional[str]:
        if not isinstance(event.data, ResponseTextDeltaEvent):
            return None
        return MessageDeltaEvent(delta=event.data.delta).serialize()

    def _handle_run_item(self, event: RunItemStreamEvent) -> Optional[str]:
        match event.name:
            case "handoff_occured":
                return AgentChangedEvent(
                    current_agent=event.item.target_agent.name
                ).serialize()
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
                ).serialize()
            case "tool_called":
                return ToolCalledEvent(
                    args=event.item.raw_item.arguments,
                    tool_name=event.item.raw_item.name,
                    tool_call_id=event.item.raw_item.call_id,
                ).serialize()
            case "tool_output":
                return ToolCallOutputEvent(
                    output=event.item.raw_item.get("output"),
                    call_id=event.item.raw_item.get("call_id"),
                ).serialize()
            case _:
                return None

    async def stream(self) -> str:
         async for event in self.iterator():
            print(event)
            result = None
            match event:
                case AgentUpdatedStreamEvent():
                    result = self._handle_agent_updated(event)
                case RawResponsesStreamEvent():
                    result = self._handle_raw_response(event)
                case RunItemStreamEvent():
                    result = self._handle_run_item(event)
             
            if result is not None:
               yield result
