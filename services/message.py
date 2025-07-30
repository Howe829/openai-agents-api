from uuid import UUID
from database import get_session
from models.message import Message
from typing import Optional
from sqlmodel import select, asc, desc, delete, func
from schemas.message import MessageFilter


class MessageService:
    @classmethod
    def create_message(
        cls,
        role: str,
        content: str,
        conversation_id: str,
        agent: Optional[str] = None,
        file_id: Optional[str] = None,
        think: Optional[str] = None,
    ) -> Message:
        message = Message(
            role=role,
            content=content,
            conversation_id=conversation_id,
            agent=agent,
            file_id=file_id,
            think=think,
        )
        with get_session() as session:
            session.add(message)
            session.commit()
            session.refresh(message)
        return message

    @classmethod
    def update_message(cls, message_id: UUID, content: Optional[str]) -> Message:
        message = cls.ensure_message(message_id=message_id)
        with get_session() as session:
            message.content = content or message.content
            session.add(message)
            session.commit()
            session.refresh(message)
        return message

    @classmethod
    def delete_message(cls, message_id: UUID) -> Message:
        with get_session() as session:
            message = cls.ensure_message(message_id=message_id)
            session.delete(message)
            session.commit()
            return Message

    @classmethod
    def delete_messages(cls, message_ids: list[UUID]) -> None:
        with get_session() as session:
            stmt = delete(Message).where(Message.id.in_(message_ids))
            session.exec(stmt)
            session.commit()

    @staticmethod
    def _get_filter_query(query, filter: Optional[MessageFilter] = None):
        if filter is None:
            return query
        if filter.id:
            query = query.where(Message.id == UUID(str(filter.id)))
        if filter.q:
            query = query.where(Message.content.contains(filter.q))
        return query

    @staticmethod
    def _get_sort_query(
        query, sort_field: Optional[str] = None, sort_order: Optional[str] = None
    ):
        if not sort_field or sort_field == "id":
            query = query.order_by(desc(Message.created_at))
            return query
        sort_col = getattr(Message, sort_field, None)
        if sort_col is None:
            return query
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_col))
            return query
        query = query.order_by(asc(sort_col))
        return query

    @classmethod
    def get_messages(
        cls,
        filter: Optional[MessageFilter] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = "asc",
        page: int = 1,
        per_page: int = 10,
    ) -> list[Message]:
        query = select(Message)

        query = cls._get_filter_query(query, filter=filter)

        query = cls._get_sort_query(query, sort_field=sort_field, sort_order=sort_order)

        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        with get_session() as session:
            return session.exec(query).all()

    @classmethod
    def get_messages_count(
        cls,
        filter: Optional[MessageFilter] = None,
    ) -> list[Message]:
        query = select(func.count()).select_from(Message)

        query = cls._get_filter_query(query, filter=filter)

        with get_session() as session:
            return session.exec(query).one()

    @classmethod
    def get_message(cls, message_id: UUID) -> Optional[Message]:
        with get_session() as session:
            return session.exec(
                select(Message).where(Message.id == message_id)
            ).one_or_none()

    @classmethod
    def get_messages_by_conversation_id(cls, conversation_id: UUID) -> list[Message]:
        with get_session() as session:
            return session.exec(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(asc(Message.created_at))
            ).all()

    @classmethod
    def ensure_message(cls, message_id: UUID) -> Message:
        message = cls.get_message(message_id=message_id)
        if message is None:
            raise ValueError(f"Message not found Id:{message_id}")
        return message
