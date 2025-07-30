import pytest
from services.conversation import ConversationService


@pytest.fixture
def test_conversations(patch_engine):
    conversations = []
    for i in range(10):
        conversations.append(
            ConversationService.create_conversation(f"Name-{i}", {"file_id": "1234"})
        )
    return conversations


@pytest.fixture
def test_conversation(patch_engine):
    return ConversationService.create_conversation(
        "test_conversation", {"file_id": "1234"}
    )


def test_get_conversations(test_conversations):
    conversations = ConversationService.get_conversations(per_page=5)
    assert len(conversations) == 5


@pytest.mark.parametrize(
    "name, expected_name ",
    [
        (None, "test_conversation"),
        ("updated_name", "updated_name"),
    ],
)
def test_update_conversation(test_conversation, name, expected_name):
    conversation = ConversationService.update_conversation(test_conversation.id, name)
    assert conversation.name == expected_name


def test_delete_conversation(test_conversation):
    ConversationService.delete_conversation(test_conversation.id)
    assert ConversationService.get_conversation(test_conversation.id) == None
