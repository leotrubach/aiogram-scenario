from typing import Union, Dict, Optional

from aiogram.types.update import (Message, CallbackQuery, InlineQuery, ChosenInlineResult,
                                  ShippingQuery, PreCheckoutQuery, Poll, PollAnswer)

from .state import BaseState


TelegramBotAPIEventType = Union[Message, CallbackQuery, InlineQuery, ChosenInlineResult,
                                ShippingQuery, PreCheckoutQuery, Poll, PollAnswer]
TransitionsType = Dict[BaseState, Dict[str, Dict[Optional[str], BaseState]]]
RawTransitionsType = Dict[str, Dict[str, Dict[Optional[str], str]]]
