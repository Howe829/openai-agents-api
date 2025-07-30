from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class MessageFilter(BaseModel):
    q: Optional[str] = None
    id: Optional[UUID] = None
