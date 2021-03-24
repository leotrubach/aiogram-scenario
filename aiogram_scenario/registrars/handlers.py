import logging
from typing import Callable

from aiogram import Dispatcher

from aiogram_scenario.fsm.state import BaseState
from aiogram_scenario.fsm.states_mapping import StatesMapping


logger = logging.getLogger(__name__)


def _log_registration_handler_on_state(name: str, handler_type: str, state) -> None:

    logger.debug(f"Handler {name!r} (type={handler_type!r}) is registered on state: {state!r}!")


class HandlersRegistrar:

    def __init__(self, dispatcher: Dispatcher, state: BaseState, states_mapping: StatesMapping):

        self._dispatcher = dispatcher
        self._state = state
        self._states_mapping = states_mapping

    def register_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                 content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                  content_types=content_types, state=self._state_value,
                                                  run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "message", self._state_value)

    def register_callback_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_callback_query_handler(callback, *custom_filters, state=self._state_value,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "callback_query", self._state_value)

    def register_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                      content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                       content_types=content_types, state=self._state_value,
                                                       run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "channel_post", self._state_value)

    def register_chosen_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_chosen_inline_handler(callback, *custom_filters, state=self._state_value,
                                                        run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "chosen_inline", self._state_value)

    def register_edited_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                             content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                              regexp=regexp, content_types=content_types,
                                                              state=self._state_value, run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "edited_channel_post", self._state_value)

    def register_edited_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                        content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                         content_types=content_types, state=self._state_value,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "edited_message", self._state_value)

    def register_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_inline_handler(callback, *custom_filters, state=self._state_value,
                                                 run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "inline", self._state_value)

    def register_pre_checkout_query_handler(self, callback: Callable,
                                            *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_pre_checkout_query_handler(callback, *custom_filters, state=self._state_value,
                                                             run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "pre_checkout_query", self._state_value)

    def register_shipping_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_shipping_query_handler(callback, *custom_filters, state=self._state_value,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "shipping_query", self._state_value)

    @property
    def _state_value(self):

        return self._states_mapping.get_value(self._state)
