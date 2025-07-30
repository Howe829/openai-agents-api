import pendulum
from datetime import datetime
from typing import Optional
from sqlmodel import Field


class SoftDeleteMixin:
    is_deleted: Optional[bool] = Field(
        default=False,
        sa_column_kwargs={"nullable": False},
    )


def utc_now():
    return pendulum.now("UTC")


class TimestampMixin:
    created_at: Optional[datetime] = Field(
        default_factory=utc_now,
        sa_column_kwargs={"nullable": False},
    )
    updated_at: Optional[datetime] = Field(
        default_factory=utc_now,
        sa_column_kwargs={"nullable": False, "onupdate": utc_now},
    )
