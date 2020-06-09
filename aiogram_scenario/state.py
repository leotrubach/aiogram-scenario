from __future__ import annotations
from abc import ABC, abstractmethod

from aiogram import Dispatcher


class AbstractState(ABC):
    """ An abstract state class, used to define eigenstates.

        To describe your own state:
            - Inherit from this class.
            - Define asynchronous handlers.
            - Register the new handlers in the register_handlers abstract method.
            - Set the transition logic in the process_transition method.
    """

    def __init__(self):

        self.name = self.__class__.__name__

    async def process_transition(self, *args) -> None:
        """ Performs state transition logic.
            It has all the same arguments as the handler.
        """

        pass

    @abstractmethod
    def register_handlers(self, registrar: HandlersRegistrar) -> None:
        """ Registers state handlers. """

        pass


class HandlersRegistrar:
    """ Handlers registrar, used to register handlers for a specific state. """

    def __init__(self, dispatcher: Dispatcher, state: AbstractState):

        self._dispatcher = dispatcher
        self._state = state

    def register_message_handler(self, callback, *custom_filters, commands=None, regexp=None, content_types=None,
                                 run_task=None, **kwargs) -> None:
        self._dispatcher.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                  content_types=content_types, state=self._state.name,
                                                  run_task=run_task, **kwargs)

    def register_callback_query_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        self._dispatcher.register_callback_query_handler(callback, *custom_filters, state=self._state.name,
                                                         run_task=run_task, **kwargs)

    def register_channel_post_handler(self, callback, *custom_filters, commands=None, regexp=None,
                                      content_types=None, run_task=None, **kwargs) -> None:
        self._dispatcher.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                       content_types=content_types, state=self._state.name,
                                                       run_task=run_task, **kwargs)

    def register_chosen_inline_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        self._dispatcher.register_chosen_inline_handler(callback, *custom_filters, state=self._state.name,
                                                        run_task=run_task, **kwargs)

    def register_edited_channel_post_handler(self, callback, *custom_filters, commands=None, regexp=None,
                                             content_types=None, run_task=None, **kwargs) -> None:
        self._dispatcher.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                              regexp=regexp, content_types=content_types,
                                                              state=self._state.name, run_task=run_task, **kwargs)

    def register_edited_message_handler(self, callback, *custom_filters, commands=None, regexp=None,
                                        content_types=None, run_task=None, **kwargs) -> None:
        self._dispatcher.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                         content_types=content_types, state=self._state.name,
                                                         run_task=run_task, **kwargs)

    def register_inline_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        self._dispatcher.register_inline_handler(callback, *custom_filters, state=self._state.name,
                                                 run_task=run_task, **kwargs)

    def register_pre_checkout_query_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        self._dispatcher.register_pre_checkout_query_handler(callback, *custom_filters, state=self._state.name,
                                                             run_task=run_task, **kwargs)

    def register_shipping_query_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        self._dispatcher.register_shipping_query_handler(callback, *custom_filters, state=self._state.name,
                                                         run_task=run_task, **kwargs)
