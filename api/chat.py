import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from schemas.chat import ChatRequest
from agents import (
    Agent,
    Runner,
)
from _agents.context import ConversationState, SQLConversationStore, AgentContext
from _agents.triage import triage_agent
from _agents.events import EventName, NewMessageEvent
from services.conversation import ConversationService
from services.message import MessageService
from loguru import logger
from _agents.adapter import StreamEventAdapter

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

    def handle_new_message_event(event: NewMessageEvent):
        MessageService.create_message(
            role="assistant",
            content=event.content,
            think=event.think,
            conversation_id=conversation.id,
        )

    result = Runner.run_streamed(
        current_agent, [message.dict() for message in messages], context=state.context
    )

    adapter = StreamEventAdapter(event_interator=result.stream_events())

    adapter.register_handler(EventName.NEW_MESSAGE_EVENT, handle_new_message_event)

    return StreamingResponse(adapter.stream_events(), media_type="application/x-ndjson")
