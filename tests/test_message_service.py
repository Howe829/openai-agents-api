import pytest
from services.message import MessageService
from services.conversation import ConversationService
from services.file import (
    FileService,
)  # Do not delete, it has to initialize File model in the db


@pytest.fixture
def test_conversation(patch_engine):
    return ConversationService.create_conversation("name", {})


@pytest.fixture
def test_messages(test_conversation):
    messages = []
    for i in range(10):
        messages.append(
            MessageService.create_message(
                role="user", content=f"Name-{i}", conversation_id=test_conversation.id
            )
        )
    return messages


@pytest.fixture
def test_message(test_conversation):
    return MessageService.create_message(
        role="user", content="test_message", conversation_id=test_conversation.id
    )


def test_get_messages(test_messages):
    messages = MessageService.get_messages(per_page=5)
    assert len(messages) == 5


@pytest.mark.parametrize(
    "content, expected_content ",
    [
        (None, "test_message"),
        ("updated_name", "updated_name"),
    ],
)
def test_update_message(test_message, content, expected_content):
    message = MessageService.update_message(test_message.id, content)
    assert message.content == expected_content


def test_delete_message(test_message):
    MessageService.delete_message(test_message.id)
    assert MessageService.get_message(test_message.id) == None
