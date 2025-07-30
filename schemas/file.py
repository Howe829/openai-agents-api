from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class FileFilter(BaseModel):
    q: Optional[str] = None
    id: Optional[UUID] = None
    name: Optional[str] = None
