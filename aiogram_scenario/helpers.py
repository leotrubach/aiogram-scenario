import inspect
from typing import Callable, Union

from aiogram.types.update import (Message, CallbackQuery, InlineQuery, ChosenInlineResult,
                                  ShippingQuery, PreCheckoutQuery, Poll, PollAnswer)


EVENT_UNION_TYPE = Union[Message, CallbackQuery, InlineQuery, ChosenInlineResult,
                         ShippingQuery, PreCheckoutQuery, Poll, PollAnswer]


def get_existing_kwargs(callback: Callable,
                        check_varkw: bool = False,
                        **kwargs: dict) -> dict:

    spec = inspect.getfullargspec(callback)
    if check_varkw and (spec.varkw is not None):
        return kwargs

    return {k: v for k, v in kwargs.items() if k in set(spec.args + spec.kwonlyargs)}
