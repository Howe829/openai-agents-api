from fastapi import APIRouter
from uuid import UUID
from services.conversation import ConversationService
from _agents.context import AgentContext

from schemas.conversation import NewConversationResponse

router = APIRouter(prefix="/conversation")


@router.post("/new", response_model=NewConversationResponse)
async def new_conversation():
    ctx = AgentContext()
    state = {
        "context": ctx.model_dump(),
        "current_agent": None,
    }
    conversation = ConversationService.create_conversation(
        "New Conversation", state=state
    )
    return NewConversationResponse(id=str(conversation.id), name=conversation.name)


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: UUID):
    return ConversationService.get_conversation(conversation_id)
