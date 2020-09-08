from typing import Optional
import logging

from aiogram.dispatcher.handler import current_handler, ctx_data
from aiogram.types import Update, User, Chat

from .fsm import FiniteStateMachine
from aiogram_scenario.helpers import EVENT_UNION_TYPE


logger = logging.getLogger(__name__)
_UPDATE_TYPES = (
    "message",
    "callback_query",
    "inline_query",
    "edited_message",
    "channel_post",
    "edited_channel_post",
    "chosen_inline_result",
    "shipping_query",
    "pre_checkout_query",
    "poll",
    "poll_answer"
)


def get_current_user_id() -> Optional[int]:

    user = User.get_current()
    user_id = user.id if user is not None else None
    return user_id


def get_current_chat_id() -> Optional[int]:

    chat = Chat.get_current()
    chat_id = chat.id if chat is not None else None
    return chat_id


def get_current_event() -> EVENT_UNION_TYPE:

    update = Update.get_current()
    for event_type_attr in _UPDATE_TYPES:
        event = getattr(update, event_type_attr)
        if event is not None:
            return event

    raise RuntimeError("no event!")


class FSMTrigger:

    __slots__ = ("_fsm",)

    def __init__(self, fsm: FiniteStateMachine):

        self._fsm = fsm

    async def go_next(self) -> None:

        user_id = get_current_user_id()
        chat_id = get_current_chat_id()

        logger.debug("FSM received a request to move to next state "
                     f"({user_id=}, {chat_id=})...")

        await self._fsm.execute_next_transition(
            trigger_func=current_handler.get(),
            event=get_current_event(),
            context_kwargs=ctx_data.get(),
            user_id=user_id,
            chat_id=chat_id
        )

    async def go_back(self) -> None:

        user_id = get_current_user_id()
        chat_id = get_current_chat_id()

        logger.debug("FSM received a request to move to previous state "
                     f"({user_id=}, {chat_id=})...")

        await self._fsm.execute_back_transition(
            event=get_current_event(),
            context_kwargs=ctx_data.get(),
            user_id=user_id,
            chat_id=chat_id
        )
