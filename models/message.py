from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from typing import Optional
from models.mixin import SoftDeleteMixin, TimestampMixin
from sqlalchemy.dialects.sqlite import JSON
import pendulum


class Message(SQLModel, TimestampMixin, SoftDeleteMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    role: str
    agent: Optional[str] = Field(default=None)
    think: Optional[str] = Field(default=None)
    conversation_id: UUID = Field(foreign_key="conversation.id")
    file_id: Optional[UUID] = Field(default=None, foreign_key="file.id")

    def dict(self):
        return {
            "role": self.role,
            "content": self.content,
        }

    def to_dict(self):
        return {
            "id": str(self.id),
            "role": self.role,
            "content": self.content,
            "agent": self.agent,
            "created_at": pendulum.instance(self.created_at).timestamp(),
        }
