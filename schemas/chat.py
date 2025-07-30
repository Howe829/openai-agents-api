from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    file_id: Optional[UUID] = None
    message: str
