from sqlmodel import Field, SQLModel
import uuid
import pendulum
from config import settings
from models.mixin import SoftDeleteMixin, TimestampMixin


class File(SQLModel, TimestampMixin, SoftDeleteMixin, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, description="File Id"
    )
    name: str = Field(..., description="original file name")
    path: str = Field(..., description="save path")
    size: int = Field(..., description="file size")
    content_type: str = Field(..., description="mime type")

    def dump(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "created_at": pendulum.instance(self.created_at)
            .in_timezone(settings.TIMEZONE)
            .to_iso8601_string(),
            "updated_at": pendulum.instance(self.updated_at)
            .in_timezone(settings.TIMEZONE)
            .to_iso8601_string(),
        }
