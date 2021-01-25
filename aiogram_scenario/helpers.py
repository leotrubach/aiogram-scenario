import inspect
from typing import Callable, Union, Optional, Tuple

from aiogram.types.update import (Message, CallbackQuery, InlineQuery, ChosenInlineResult,
                                  ShippingQuery, PreCheckoutQuery, Poll, PollAnswer)


EventUnionType = Union[Message, CallbackQuery, InlineQuery, ChosenInlineResult,
                       ShippingQuery, PreCheckoutQuery, Poll, PollAnswer]


def get_existing_kwargs(callback: Callable, check_varkw: bool = False, **kwargs) -> dict:

    spec = inspect.getfullargspec(callback)
    if check_varkw and (spec.varkw is not None):
        return kwargs

    return {k: v for k, v in kwargs.items() if k in set(spec.args + spec.kwonlyargs)}


def resolve_address(*, chat_id: Optional[int] = None, user_id: Optional[int] = None) -> Tuple[int, int]:

    if (chat_id is None) and (user_id is None):
        raise ValueError("'chat_id' or 'user_id' parameter is required but no one is provided!")

    return chat_id or user_id, user_id or chat_id
