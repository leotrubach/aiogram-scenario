from __future__ import annotations
from abc import ABC, abstractmethod
import logging

from aiogram import Dispatcher


logger = logging.getLogger(__name__)


def _log_registration_handler(state, callback, handler_type):

    logger.debug(f"For the state {state!r}, a {handler_type}_handler is registered: {callback!r}")


class AbstractState(ABC):
    """ An abstract target_state class, used to define eigenstates.

        To describe your own target_state:
            - Inherit from this class.
            - Define asynchronous handlers.
            - Register the new handlers in the register_handlers abstract method.
            - Set the transition logic in the process_transition method.
    """

    def __init__(self):

        self.name = self.__class__.__name__

    async def process_transition(self, *args, **kwargs) -> None:
        """ Performs target_state transition logic.
            It has all the same arguments as the handler.
        """

        pass

    @abstractmethod
    def register_handlers(self, registrar: HandlersRegistrar) -> None:
        """ Registers target_state handlers. """

        pass


class HandlersRegistrar:
    """ Handlers registrar, used to register handlers for a specific target_state. """

    def __init__(self, dispatcher: Dispatcher, state: AbstractState):

        self._dispatcher = dispatcher
        self._state = state

    def register_message_handler(self, callback, *custom_filters, commands=None, regexp=None, content_types=None,
                                 run_task=None, **kwargs) -> None:
        self._dispatcher.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                  content_types=content_types, state=self._state.name,
                                                  run_task=run_task, **kwargs)
        _log_registration_handler(self._state, callback, "message")

    def register_callback_query_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        self._dispatcher.register_callback_query_handler(callback, *custom_filters, state=self._state.name,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler(self._state, callback, "callback_query")

    def register_channel_post_handler(self, callback, *custom_filters, commands=None, regexp=None,
                                      content_types=None, run_task=None, **kwargs) -> None:
        self._dispatcher.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                       content_types=content_types, state=self._state.name,
                                                       run_task=run_task, **kwargs)
        _log_registration_handler(self._state, callback, "channel_post")

    def register_chosen_inline_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        self._dispatcher.register_chosen_inline_handler(callback, *custom_filters, state=self._state.name,
                                                        run_task=run_task, **kwargs)
        _log_registration_handler(self._state, callback, "chosen_inline")

    def register_edited_channel_post_handler(self, callback, *custom_filters, commands=None, regexp=None,
                                             content_types=None, run_task=None, **kwargs) -> None:
        self._dispatcher.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                              regexp=regexp, content_types=content_types,
                                                              state=self._state.name, run_task=run_task, **kwargs)
        _log_registration_handler(self._state, callback, "edited_channel_post")

    def register_edited_message_handler(self, callback, *custom_filters, commands=None, regexp=None,
                                        content_types=None, run_task=None, **kwargs) -> None:
        self._dispatcher.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                         content_types=content_types, state=self._state.name,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler(self._state, callback, "edited_message")

    def register_inline_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        self._dispatcher.register_inline_handler(callback, *custom_filters, state=self._state.name,
                                                 run_task=run_task, **kwargs)
        _log_registration_handler(self._state, callback, "inline")

    def register_pre_checkout_query_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        self._dispatcher.register_pre_checkout_query_handler(callback, *custom_filters, state=self._state.name,
                                                             run_task=run_task, **kwargs)
        _log_registration_handler(self._state, callback, "pre_checkout_query")

    def register_shipping_query_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        self._dispatcher.register_shipping_query_handler(callback, *custom_filters, state=self._state.name,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler(self._state, callback, "shipping_query")
