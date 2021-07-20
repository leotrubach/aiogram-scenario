import pytest

from aiogram.types import Chat, User
from aiogram.dispatcher.handler import current_handler


@pytest.fixture()
def chat_id():

    return -1001234567890


@pytest.fixture()
def user_id():

    return 1234567890


@pytest.fixture()
def event_stub():

    return object()


@pytest.fixture()
def scene_data_stub():

    return object()


@pytest.fixture()
def chat(chat_id):

    chat_ = Chat()
    chat_.id = chat_id
    # noinspection PyUnresolvedReferences
    # noinspection PyProtectedMember
    context = Chat._ContextInstanceMixin__context_instance
    token = context.set(chat_)

    yield chat_

    context.reset(token)


@pytest.fixture()
def user(user_id):

    user_ = User()
    user_.id = user_id
    # noinspection PyUnresolvedReferences
    # noinspection PyProtectedMember
    context = User._ContextInstanceMixin__context_instance
    token = context.set(user_)

    yield user_

    context.reset(token)


@pytest.fixture()
def handler():

    # noinspection PyUnusedLocal
    async def handler_(event):
        pass

    token = current_handler.set(handler_)

    yield handler_

    current_handler.reset(token)
