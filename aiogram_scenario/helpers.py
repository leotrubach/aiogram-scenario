import inspect
from typing import Callable

from aiogram.types import Update


EVENT_TYPES = (
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


def get_existing_kwargs(callback: Callable,
                        check_varkw: bool = False,
                        **kwargs: dict) -> dict:

    spec = inspect.getfullargspec(callback)
    if check_varkw and (spec.varkw is not None):
        return kwargs

    return {k: v for k, v in kwargs.items() if k in spec.args}


def get_current_event():

    update = Update.get_current()
    for event_type_attr in EVENT_TYPES:
        event = getattr(update, event_type_attr)
        if event is not None:
            return event
