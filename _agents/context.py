from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from services.conversation import ConversationService


class AgentContext(BaseModel):
    """Context for agents."""

    current_file_id: str | None = None
    user_id: str | None = None


class ConversationStore:
    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        pass

    def save(self, conversation_id: str, state: Dict[str, Any]):
        pass


class ConversationState(BaseModel):
    context: AgentContext
    current_agent: Optional[str] = Field(default=None)

    def to_dict(self):
        return {
            "context": self.context.model_dump(),
            "current_agent": self.current_agent,
        }


class SQLConversationStore(ConversationStore):
    def get(self, conversation_id: UUID) -> Optional[ConversationState]:
        conversation = ConversationService.get_conversation(conversation_id)
        if not conversation:
            return None
        return conversation.state

    def save(self, conversation_id: UUID, state: ConversationState):
        conversation = ConversationService.get_conversation(conversation_id)
        if not conversation:
            return
        ConversationService.update_conversation(
            conversation_id=conversation_id, state=state.model_dump()
        )
