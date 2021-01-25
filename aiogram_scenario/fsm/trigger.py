from typing import Optional
import logging

from aiogram.dispatcher.handler import current_handler, ctx_data
from aiogram.types import (User, Chat, Message, CallbackQuery, InlineQuery, ChosenInlineResult,
                           ShippingQuery, PreCheckoutQuery, Poll, PollAnswer)

from .fsm import FSM
from aiogram_scenario import helpers
from aiogram_scenario.helpers import EventUnionType


logger = logging.getLogger(__name__)


def _get_current_chat_id() -> Optional[int]:

    chat = Chat.get_current()
    chat_id = chat.id if chat is not None else None
    return chat_id


def _get_current_user_id() -> Optional[int]:

    user = User.get_current()
    user_id = user.id if user is not None else None
    return user_id


def _get_current_event() -> EventUnionType:

    for EventType in (Message, CallbackQuery, InlineQuery, ChosenInlineResult,
                      ShippingQuery, PreCheckoutQuery, Poll, PollAnswer):
        event = EventType.get_current()
        if event is not None:
            return event

    raise RuntimeError("no current event!")


class FSMTrigger:

    __slots__ = ("_fsm",)

    def __init__(self, fsm: FSM):

        self._fsm = fsm

    async def go_next(self) -> None:

        chat_id = _get_current_chat_id()
        user_id = _get_current_user_id()
        chat_id, user_id = helpers.resolve_address(chat_id=chat_id, user_id=user_id)

        logger.debug("FSM received a request to move to next state "
                     f"({chat_id=}, {user_id=})...")

        await self._fsm.execute_next_transition(
            trigger=current_handler.get(),
            event=_get_current_event(),
            context_kwargs=ctx_data.get(),
            chat_id=chat_id,
            user_id=user_id
        )

    async def go_back(self) -> None:

        chat_id = _get_current_chat_id()
        user_id = _get_current_user_id()
        chat_id, user_id = helpers.resolve_address(chat_id=chat_id, user_id=user_id)

        logger.debug("FSM received a request to move to previous state "
                     f"({chat_id=}, {user_id=})...")

        await self._fsm.execute_back_transition(
            event=_get_current_event(),
            context_kwargs=ctx_data.get(),
            chat_id=chat_id,
            user_id=user_id
        )
