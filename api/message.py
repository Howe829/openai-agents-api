from fastapi import APIRouter
from uuid import UUID
from services.message import MessageService


router = APIRouter(prefix="/message")


@router.get("/list")
async def get_messages(conversation_id: UUID):
    messages = MessageService.get_messages_by_conversation_id(conversation_id)
    file_ids = [m.file_id for m in messages]
    files = FileService.get_files_by_file_ids(file_ids=file_ids)
    file_id_mapping = {f.id: {"file_id": f.id, "filename": f.name} for f in files}
    data = []
    for message in messages:
        m = message.model_dump()
        data.append({**m, "file": file_id_mapping.get(message.file_id)})
    return data
