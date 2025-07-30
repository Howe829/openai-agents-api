from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
import json
from models.mixin import TimestampMixin, SoftDeleteMixin
from sqlalchemy.dialects.sqlite import JSON


class Conversation(SQLModel, TimestampMixin, SoftDeleteMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    state: Optional[dict] = Field(default=None, sa_type=JSON)

    def model_dump_json(self) -> str:
        return json.dumps(
            {"id": str(self.id), "name": self.name, "state": self.state},
            ensure_ascii=False,
        )
