import logging
from typing import Callable, Optional

from aiogram import Dispatcher


logger = logging.getLogger(__name__)


def _log_registration_handler_on_state(name: str, handler_type: str, state: str) -> None:

    logger.debug(f"Handler '{name}' (type='{handler_type}') is registered on state: '{state}'!")


class HandlersRegistrar:

    def __init__(self, dispatcher: Dispatcher, state: Optional[str]):

        self._dispatcher = dispatcher
        self._state = state

    def register_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                 content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                  content_types=content_types, state=self._state,
                                                  run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "message", str(self._state))

    def register_callback_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_callback_query_handler(callback, *custom_filters, state=self._state,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "callback_query", str(self._state))

    def register_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                      content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                       content_types=content_types, state=self._state,
                                                       run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "channel_post", str(self._state))

    def register_chosen_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_chosen_inline_handler(callback, *custom_filters, state=self._state,
                                                        run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "chosen_inline", str(self._state))

    def register_edited_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                             content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                              regexp=regexp, content_types=content_types,
                                                              state=self._state, run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "edited_channel_post", str(self._state))

    def register_edited_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                        content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                         content_types=content_types, state=self._state,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "edited_message", str(self._state))

    def register_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_inline_handler(callback, *custom_filters, state=self._state,
                                                 run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "inline", str(self._state))

    def register_pre_checkout_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_pre_checkout_query_handler(callback, *custom_filters, state=self._state,
                                                             run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "pre_checkout_query", str(self._state))

    def register_shipping_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_shipping_query_handler(callback, *custom_filters, state=self._state,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "shipping_query", str(self._state))
