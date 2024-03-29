from __future__ import annotations
from typing import Callable, Iterable, Set, Optional, TYPE_CHECKING
import logging

from aiogram import Dispatcher

from aiogram_scenario.fsm.states_mapping import StatesMapping
from .handlers import HandlersRegistrar
if TYPE_CHECKING:
    from aiogram_scenario.fsm.state import BaseState


logger = logging.getLogger(__name__)


def _log_registration_handler(name: str, handler_type: str) -> None:

    logger.debug(f"Handler {name!r} (type={handler_type!r}) is registered!")


class FSMHandlersRegistrar:

    def __init__(self, dispatcher: Dispatcher, states_mapping: StatesMapping):

        self._dispatcher = dispatcher
        self._states_mapping = states_mapping

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

    def register_states_handlers(self, states: Iterable[BaseState], data: Optional[dict] = None) -> None:

        if data is None:
            data = {}

        for state in states:
            registrar = self._get_state_registrar(state)
            state.register_handlers(registrar, data)

    def register_message_handler(self, callback: Callable, states: Iterable[BaseState], *custom_filters,
                                 commands=None, regexp=None, content_types=None, run_task=None, **kwargs) -> None:

        for state in states:
            registrar = self._get_state_registrar(state)
            registrar.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                               content_types=content_types, run_task=run_task, **kwargs)

    def register_callback_query_handler(self, callback: Callable, states: Iterable[BaseState], *custom_filters,
                                        run_task=None, **kwargs) -> None:

        for state in states:
            registrar = self._get_state_registrar(state)
            registrar.register_callback_query_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_channel_post_handler(self, callback: Callable, states: Iterable[BaseState], *custom_filters,
                                      commands=None, regexp=None, content_types=None, run_task=None, **kwargs) -> None:

        for state in states:
            registrar = self._get_state_registrar(state)
            registrar.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                    content_types=content_types, run_task=run_task, **kwargs)

    def register_chosen_inline_handler(self, callback: Callable, states: Iterable[BaseState], *custom_filters,
                                       run_task=None, **kwargs) -> None:

        for state in states:
            registrar = self._get_state_registrar(state)
            registrar.register_chosen_inline_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_edited_channel_post_handler(self, callback: Callable, states: Iterable[BaseState], *custom_filters,
                                             commands=None, regexp=None, content_types=None,
                                             run_task=None, **kwargs) -> None:

        for state in states:
            registrar = self._get_state_registrar(state)
            registrar.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                           regexp=regexp, content_types=content_types,
                                                           run_task=run_task, **kwargs)

    def register_edited_message_handler(self, callback: Callable, states: Iterable[BaseState], *custom_filters,
                                        commands=None, regexp=None, content_types=None,
                                        run_task=None, **kwargs) -> None:

        for state in states:
            registrar = self._get_state_registrar(state)
            registrar.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                      content_types=content_types, run_task=run_task, **kwargs)

    def register_inline_handler(self, callback: Callable, states: Iterable[BaseState], *custom_filters,
                                run_task=None, **kwargs) -> None:

        for state in states:
            registrar = self._get_state_registrar(state)
            registrar.register_inline_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_pre_checkout_query_handler(self, callback: Callable, states: Iterable[BaseState], *custom_filters,
                                            run_task=None, **kwargs) -> None:

        for state in states:
            registrar = self._get_state_registrar(state)
            registrar.register_pre_checkout_query_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_shipping_query_handler(self, callback: Callable, states: Iterable[BaseState], *custom_filters,
                                        run_task=None, **kwargs) -> None:

        for state in states:
            registrar = self._get_state_registrar(state)
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

    def _get_state_registrar(self, state: BaseState) -> HandlersRegistrar:

        return HandlersRegistrar(self._dispatcher, state, self._states_mapping)
