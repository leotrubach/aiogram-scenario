from typing import Callable

from aiogram.dispatcher.handler import current_handler
from aiogram.types import Chat, User

from aiogramscenario import errors


def get_chat_id_with_context() -> int:

    chat = Chat.get_current()
    if chat is None:
        raise errors.ContextVarNotSet("Chat is not set!")

    return chat.id


def get_user_id_with_context() -> int:

    user = User.get_current()
    if user is None:
        raise errors.ContextVarNotSet("User is not set!")

    return user.id


def get_handler_with_context() -> Callable:

    try:
        handler = current_handler.get()
    except LookupError:
        raise errors.ContextVarNotSet("handler is not set!") from None

    return handler
