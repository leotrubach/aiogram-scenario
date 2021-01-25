from typing import Callable, Collection, List, Set, Optional
import logging

from aiogram import Dispatcher

from .fsm.state import BaseState


logger = logging.getLogger(__name__)


def _log_registration_handler_on_state(name: str, handler_type: str, state: str) -> None:

    logger.debug(f"Handler '{name}' (type='{handler_type}') is registered on state: '{state}'!")


def _log_registration_handler(name: str, handler_type: str) -> None:

    logger.debug(f"Handler '{name}' (type='{handler_type}') is registered!")


class HandlersRegistrar:

    def __init__(self, dispatcher: Dispatcher, state: BaseState):

        self._dispatcher = dispatcher
        self._state = state

    def register_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                 content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                  content_types=content_types, state=self._state.value,
                                                  run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "message", str(self._state))

    def register_callback_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_callback_query_handler(callback, *custom_filters, state=self._state.value,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "callback_query", str(self._state))

    def register_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                      content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                       content_types=content_types, state=self._state.value,
                                                       run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "channel_post", str(self._state))

    def register_chosen_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_chosen_inline_handler(callback, *custom_filters, state=self._state.value,
                                                        run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "chosen_inline", str(self._state))

    def register_edited_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                             content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                              regexp=regexp, content_types=content_types,
                                                              state=self._state.value, run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "edited_channel_post", str(self._state))

    def register_edited_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                        content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                         content_types=content_types, state=self._state.value,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "edited_message", str(self._state))

    def register_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_inline_handler(callback, *custom_filters, state=self._state.value,
                                                 run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "inline", str(self._state))

    def register_pre_checkout_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_pre_checkout_query_handler(callback, *custom_filters, state=self._state.value,
                                                             run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "pre_checkout_query", str(self._state))

    def register_shipping_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_shipping_query_handler(callback, *custom_filters, state=self._state.value,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback.__qualname__, "shipping_query", str(self._state))


class CommonHandlersRegistrar:

    def __init__(self, dispatcher: Dispatcher):

        self._dispatcher = dispatcher

    def get_registered_handlers(self) -> Set[Callable]:

        handlers = set()
        dispatcher_handlers = (
            self._dispatcher.message_handlers,
            self._dispatcher.callback_query_handlers,
            self._dispatcher.channel_post_handlers,
            self._dispatcher.chosen_inline_result_handlers,
            self._dispatcher.edited_channel_post_handlers,
            self._dispatcher.edited_message_handlers,
            self._dispatcher.inline_query_handlers,
            self._dispatcher.pre_checkout_query_handlers,
            self._dispatcher.shipping_query_handlers,
            self._dispatcher.errors_handlers,
            self._dispatcher.poll_handlers,
            self._dispatcher.poll_answer_handlers
        )

        for handler_obj in dispatcher_handlers:
            handlers.update(handler_obj.handlers)

        return handlers

    def register_states_handlers(self, states: Collection[BaseState], data: Optional[dict] = None) -> None:

        if data is None:
            data = {}

        for state in states:
            registrar = HandlersRegistrar(self._dispatcher, state=state)
            state.register_handlers(registrar, data)

    def register_message_handler(self, callback: Callable, states: List[BaseState], *custom_filters, commands=None,
                                 regexp=None, content_types=None, run_task=None, **kwargs) -> None:

        for state in states:
            registrar = HandlersRegistrar(self._dispatcher, state)
            registrar.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                               content_types=content_types, run_task=run_task, **kwargs)

    def register_callback_query_handler(self, callback: Callable, states: List[BaseState], *custom_filters,
                                        run_task=None, **kwargs) -> None:

        for state in states:
            registrar = HandlersRegistrar(self._dispatcher, state)
            registrar.register_callback_query_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_channel_post_handler(self, callback: Callable, states: List[BaseState], *custom_filters,
                                      commands=None, regexp=None, content_types=None, run_task=None, **kwargs) -> None:

        for state in states:
            registrar = HandlersRegistrar(self._dispatcher, state)
            registrar.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                    content_types=content_types, run_task=run_task, **kwargs)

    def register_chosen_inline_handler(self, callback: Callable, states: List[BaseState], *custom_filters,
                                       run_task=None, **kwargs) -> None:

        for state in states:
            registrar = HandlersRegistrar(self._dispatcher, state)
            registrar.register_chosen_inline_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_edited_channel_post_handler(self, callback: Callable, states: List[BaseState], *custom_filters,
                                             commands=None, regexp=None, content_types=None,
                                             run_task=None, **kwargs) -> None:

        for state in states:
            registrar = HandlersRegistrar(self._dispatcher, state)
            registrar.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                           regexp=regexp, content_types=content_types,
                                                           run_task=run_task, **kwargs)

    def register_edited_message_handler(self, callback: Callable, states: List[BaseState], *custom_filters,
                                        commands=None, regexp=None, content_types=None,
                                        run_task=None, **kwargs) -> None:

        for state in states:
            registrar = HandlersRegistrar(self._dispatcher, state)
            registrar.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                      content_types=content_types, run_task=run_task, **kwargs)

    def register_inline_handler(self, callback: Callable, states: List[BaseState], *custom_filters,
                                run_task=None, **kwargs) -> None:

        for state in states:
            registrar = HandlersRegistrar(self._dispatcher, state)
            registrar.register_inline_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_pre_checkout_query_handler(self, callback: Callable, states: List[BaseState], *custom_filters,
                                            run_task=None, **kwargs) -> None:

        for state in states:
            registrar = HandlersRegistrar(self._dispatcher, state)
            registrar.register_pre_checkout_query_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_shipping_query_handler(self, callback: Callable, states: List[BaseState], *custom_filters,
                                        run_task=None, **kwargs) -> None:

        for state in states:
            registrar = HandlersRegistrar(self._dispatcher, state)
            registrar.register_shipping_query_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_errors_handler(self, callback: Callable, *custom_filters, exception=None,
                                run_task=None, **kwargs) -> None:

        self._dispatcher.register_errors_handler(callback, *custom_filters, exception=exception,
                                                 run_task=run_task, **kwargs)
        _log_registration_handler(callback.__qualname__, "errors")

    def register_poll_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_poll_handler(callback, *custom_filters, run_task=run_task, **kwargs)
        _log_registration_handler(callback.__qualname__, "poll")

    def register_poll_answer_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_poll_answer_handler(callback, *custom_filters, run_task=run_task, **kwargs)
        _log_registration_handler(callback.__qualname__, "poll_answer")
