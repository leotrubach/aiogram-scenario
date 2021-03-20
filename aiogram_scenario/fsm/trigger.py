from typing import Optional, Callable
import logging

from aiogram.dispatcher.handler import current_handler, ctx_data
from aiogram.types import User, Chat, Update

from .fsm import FSM
from .types import TelegramBotAPIEventType
from aiogram_scenario import helpers


logger = logging.getLogger(__name__)


def _get_current_chat_id() -> Optional[int]:

    chat = Chat.get_current()
    chat_id = chat.id if chat is not None else None
    return chat_id


def _get_current_user_id() -> Optional[int]:

    user = User.get_current()
    user_id = user.id if user is not None else None
    return user_id


def _get_current_event() -> TelegramBotAPIEventType:

    update = Update.get_current()
    if update is not None:
        event = (update.message or update.callback_query or update.inline_query or update.chosen_inline_result
                 or update.shipping_query or update.pre_checkout_query or update.poll or update.poll_answer)
        if event is None:
            raise RuntimeError("no current event!")
    else:
        raise RuntimeError("no current update!")

    return event


def _get_current_handler() -> Callable:

    handler = current_handler.get()
    if handler is None:
        raise RuntimeError("no current handler!")

    return handler


def _get_current_context_data() -> dict:

    data = ctx_data.get()
    if data is None:
        raise RuntimeError("no context data!")

    return data


def _get_context_items() -> tuple:

    chat_id = _get_current_chat_id()
    user_id = _get_current_user_id()
    handler = _get_current_handler()
    event = _get_current_event()
    context_data = _get_current_context_data()

    return chat_id, user_id, handler, event, context_data


class FSMTrigger:

    __slots__ = ("_fsm",)

    def __init__(self, fsm: FSM):

        self._fsm = fsm

    async def go_next(self, direction: Optional[str] = None) -> None:

        chat_id, user_id, handler, event, context_data = _get_context_items()
        chat_id, user_id = helpers.normalize_telegram_ids(chat_id=chat_id, user_id=user_id)
        handler = handler.__name__

        logger.debug(f"FSM received a request to move to next state ({chat_id=}, {user_id=})...")

        await self._fsm.execute_next_transition(chat_id=chat_id, user_id=user_id, handler=handler,
                                                direction=direction, processing_args=(event,),
                                                processing_kwargs=context_data)

    async def go_back(self) -> None:

        chat_id, user_id, _, event, context_data = _get_context_items()
        chat_id, user_id = helpers.normalize_telegram_ids(chat_id=chat_id, user_id=user_id)

        logger.debug(f"FSM received a request to move to previous state ({chat_id=}, {user_id=})...")

        await self._fsm.execute_back_transition(chat_id=chat_id, user_id=user_id, processing_args=(event,),
                                                processing_kwargs=context_data)
