from fastapi import APIRouter, Query
from uuid import UUID
from services.conversation import ConversationService
from _agents.context import AgentContext
from typing import Optional
from datetime import timezone

from schemas.conversation import NewConversationResponse, ConversationFilter

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


@router.get("/list")
async def get_conversations(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    sort_field: Optional[str] = Query(None),
    sort_order: Optional[str] = Query("desc"),
    q: Optional[str] = Query(None),
):
    filter_obj = ConversationFilter(q=q) if q else None
    conversations = ConversationService.get_conversations(
        filter=filter_obj,
        sort_field=sort_field or "updated_at",
        sort_order=sort_order,
        page=page,
        per_page=per_page,
    )
    total = ConversationService.get_conversations_count(filter=filter_obj)

    return {
        "conversations": [
            {
                "id": str(conv.id),
                "name": conv.name,
                "created_at": conv.created_at.replace(tzinfo=timezone.utc).isoformat()
                if conv.created_at
                else None,
                "updated_at": conv.updated_at.replace(tzinfo=timezone.utc).isoformat()
                if conv.updated_at
                else None,
            }
            for conv in conversations
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: UUID):
    try:
        ConversationService.delete_conversation(conversation_id)
        return {"message": "Conversation deleted successfully"}
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: UUID):
    return ConversationService.get_conversation(conversation_id)
