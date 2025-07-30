from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ConversationFilter(BaseModel):
    q: Optional[str] = None
    id: Optional[UUID] = None
    name: Optional[str] = None


class NewConversationResponse(BaseModel):
    id: UUID
    name: str
