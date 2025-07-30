from uuid import UUID
from database import get_session
from models.conversation import Conversation
from typing import Optional
from sqlmodel import select, asc, desc, delete, exists, func
from schemas.conversation import ConversationFilter


class ConversationService:
    @classmethod
    def create_conversation(
        cls, name: str = "Conversation", state: Optional[dict] = None
    ) -> Conversation:
        conversation = Conversation(name=name, state=state)
        with get_session() as session:
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        return conversation

    @classmethod
    def update_conversation(
        cls,
        conversation_id: UUID,
        name: Optional[str] = None,
        state: Optional[dict] = None,
    ) -> Conversation:
        conversation = cls.ensure_conversation(conversation_id=conversation_id)
        with get_session() as session:
            conversation.name = name or conversation.name
            conversation.state = state or conversation.state
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        return conversation

    @classmethod
    def delete_conversation(cls, conversation_id: UUID) -> Conversation:
        with get_session() as session:
            conversation = cls.ensure_conversation(conversation_id=conversation_id)
            session.delete(conversation)
            session.commit()
            return Conversation

    @classmethod
    def delete_conversations(cls, conversation_ids: list[UUID]) -> None:
        with get_session() as session:
            stmt = delete(Conversation).where(Conversation.id.in_(conversation_ids))
            session.exec(stmt)
            session.commit()

    @staticmethod
    def _get_filter_query(query, filter: Optional[ConversationFilter] = None):
        if filter is None:
            return query
        if filter.id:
            query = query.where(Conversation.id == UUID(str(filter.id)))
        if filter.name:
            query = query.where(Conversation.name == filter.name)
        if filter.q:
            query = query.where(Conversation.name.contains(filter.q))
        return query

    @staticmethod
    def _get_sort_query(
        query, sort_field: Optional[str] = None, sort_order: Optional[str] = None
    ):
        if not sort_field or sort_field == "id":
            query = query.order_by(desc(Conversation.created_at))
            return query
        sort_col = getattr(Conversation, sort_field, None)
        if sort_col is None:
            return query
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_col))
            return query
        query = query.order_by(asc(sort_col))
        return query

    @classmethod
    def get_conversations(
        cls,
        filter: Optional[ConversationFilter] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = "asc",
        page: int = 1,
        per_page: int = 10,
    ) -> list[Conversation]:
        query = select(Conversation)

        # 处理 filter 条件
        query = cls._get_filter_query(query, filter=filter)

        # 排序
        query = cls._get_sort_query(query, sort_field=sort_field, sort_order=sort_order)

        # 分页
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        with get_session() as session:
            return session.exec(query).all()

    @classmethod
    def get_conversations_count(
        cls,
        filter: Optional[ConversationFilter] = None,
    ) -> list[Conversation]:
        query = select(func.count()).select_from(Conversation)

        query = cls._get_filter_query(query, filter=filter)

        with get_session() as session:
            return session.exec(query).one()

    @classmethod
    def get_conversation(cls, conversation_id: UUID) -> Optional[Conversation]:
        with get_session() as session:
            return session.exec(
                select(Conversation).where(Conversation.id == conversation_id)
            ).one_or_none()

    @classmethod
    def ensure_conversation_name(cls, name: str) -> bool:
        with get_session() as session:
            stmt = select(exists().where(Conversation.name == name))
            return session.exec(stmt).one_or_none()

    @classmethod
    def ensure_conversation(cls, conversation_id: UUID) -> Conversation:
        conversation = cls.get_conversation(conversation_id=conversation_id)
        if conversation is None:
            raise ValueError(f"Conversation not found Id:{conversation_id}")
        return conversation
