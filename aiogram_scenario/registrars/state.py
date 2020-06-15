import logging
from typing import Union, Callable

from aiogram import Dispatcher


logger = logging.getLogger(__name__)


def _log_registration_handler(state_name: str, callback: Callable, handler_type: str) -> None:

    logger.debug(f"For the state '{state_name}', a {handler_type}_handler "
                 f"is registered: '{callback.__name__}'")


class StateRegistrar:

    def __init__(self, dispatcher: Dispatcher, state_name: Union[str, None]):

        self._dispatcher = dispatcher
        self._state_name = state_name

    def register_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                 content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                  content_types=content_types, state=self._state_name,
                                                  run_task=run_task, **kwargs)
        _log_registration_handler(self._state_name, callback, "message")

    def register_callback_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_callback_query_handler(callback, *custom_filters, state=self._state_name,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler(self._state_name, callback, "callback_query")

    def register_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                      content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                       content_types=content_types, state=self._state_name,
                                                       run_task=run_task, **kwargs)
        _log_registration_handler(self._state_name, callback, "channel_post")

    def register_chosen_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_chosen_inline_handler(callback, *custom_filters, state=self._state_name,
                                                        run_task=run_task, **kwargs)
        _log_registration_handler(self._state_name, callback, "chosen_inline")

    def register_edited_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                             content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                              regexp=regexp, content_types=content_types,
                                                              state=self._state_name, run_task=run_task, **kwargs)
        _log_registration_handler(self._state_name, callback, "edited_channel_post")

    def register_edited_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                        content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                         content_types=content_types, state=self._state_name,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler(self._state_name, callback, "edited_message")

    def register_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_inline_handler(callback, *custom_filters, state=self._state_name,
                                                 run_task=run_task, **kwargs)
        _log_registration_handler(self._state_name, callback, "inline")

    def register_pre_checkout_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_pre_checkout_query_handler(callback, *custom_filters, state=self._state_name,
                                                             run_task=run_task, **kwargs)
        _log_registration_handler(self._state_name, callback, "pre_checkout_query")

    def register_shipping_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_shipping_query_handler(callback, *custom_filters, state=self._state_name,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler(self._state_name, callback, "shipping_query")
