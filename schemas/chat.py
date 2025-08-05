from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ChatRequest(BaseModel):
    conversation_id: UUID
    file_id: Optional[UUID] = None
    message: str
