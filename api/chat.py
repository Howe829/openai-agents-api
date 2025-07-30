import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from schemas.chat import ChatRequest
from _agents.events import NewConversationEvent
from agents import (
    Agent,
    Runner,
)
from _agents.context import ConversationState, SQLConversationStore, AgentContext
from _agents.triage import triage_agent
from _agents.events import NewMessageEvent
from services.conversation import ConversationService
from services.message import MessageService
from loguru import logger
from _agents.adapter import StreamEventAdapter, StreamEventSender

router = APIRouter(prefix="/chat")


conversation_store = SQLConversationStore()

AGENTS: list[Agent] = [triage_agent]


def _get_agent_by_name(name: str):
    """Return the agent object by name."""
    agents = {agent.name: agent for agent in AGENTS}
    return agents.get(name, triage_agent)


def _get_guardrail_name(g) -> str:
    """Extract a friendly guardrail name."""
    name_attr = getattr(g, "name", None)
    if isinstance(name_attr, str) and name_attr:
        return name_attr
    guard_fn = getattr(g, "guardrail_function", None)
    if guard_fn is not None and hasattr(guard_fn, "__name__"):
        return guard_fn.__name__.replace("_", " ").title()
    fn_name = getattr(g, "__name__", None)
    if isinstance(fn_name, str) and fn_name:
        return fn_name.replace("_", " ").title()
    return str(g)


def _build_agents_list() -> List[Dict[str, Any]]:
    """Build a list of all available agents and their metadata."""

    def make_agent_dict(agent: Agent):
        return {
            "name": agent.name,
            "description": getattr(agent, "handoff_description", ""),
            "handoffs": [
                getattr(h, "agent_name", getattr(h, "name", ""))
                for h in getattr(agent, "handoffs", [])
            ],
            "tools": [
                getattr(t, "name", getattr(t, "__name__", ""))
                for t in getattr(agent, "tools", [])
            ],
            "input_guardrails": [
                _get_guardrail_name(g) for g in getattr(agent, "input_guardrails", [])
            ],
        }

    return [make_agent_dict(agent) for agent in AGENTS]


@router.get("/agents")
async def get_agents() -> List[Dict[str, Any]]:
    return _build_agents_list()


@router.post("/streaming")
async def streamable_chat_endpoint(req: ChatRequest):
    conversation = ConversationService.get_conversation(req.conversation_id)
    adapter = StreamEventAdapter()
    sender = StreamEventSender()
    if conversation is None:
        conversation = ConversationService.create_conversation(
            state=ConversationState(context=AgentContext()).to_dict(),
        )
        new_conversation_event = NewConversationEvent(
            conversation_id=str(conversation.id)
        )
        await sender.send(new_conversation_event)

    state = ConversationState(**conversation.state)
    if req.file_id:
        state.context.current_file_id = req.file_id
        ConversationService.update_conversation(conversation.id, state=state.to_dict())

    current_agent = _get_agent_by_name(state.current_agent)

    MessageService.create_message(
        role="user",
        content=req.message,
        file_id=req.file_id,
        conversation_id=conversation.id,
    )
    messages = MessageService.get_messages_by_conversation_id(
        conversation_id=conversation.id
    )

    result = Runner.run_streamed(
        current_agent, [message.dict() for message in messages], context=state.context
    )
    
    # 启动后台任务处理事件流
    async def process_events():
        try:
            async for event in result.stream_events():
                processed_event = adapter.process_event(event)
                if isinstance(processed_event, NewMessageEvent):
                    MessageService.create_message(
                        role="assistant",
                        content=processed_event.content,
                        conversation_id=conversation.id,
                        think=processed_event.think,
                    )
                await sender.send(processed_event)
        finally:
            await sender.close()
    
    # 立即启动后台任务，不等待完成
    asyncio.create_task(process_events())
    
    return StreamingResponse(sender, media_type="application/x-ndjson")
