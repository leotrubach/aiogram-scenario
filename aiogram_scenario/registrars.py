from typing import Callable, Collection, List
import logging
import functools

from aiogram import Dispatcher

from . import helpers
from aiogram_scenario.fsm.state import AbstractState


logger = logging.getLogger(__name__)


def _log_registration_handler_on_state(callback: Callable, handler_type: str, state: AbstractState):

    logger.debug(f"Handler '{callback.__qualname__}' (type='{handler_type}') is registered on state: '{state}'!")


def _log_registration_handler(callback: Callable, handler_type: str):

    logger.debug(f"Handler '{callback.__qualname__}' (type='{handler_type}') is registered!")


class Registrar:

    def __init__(self, dispatcher: Dispatcher, state: AbstractState):

        self._dispatcher = dispatcher
        self._state = state

    def register_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                 content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                  content_types=content_types, state=self._state.raw_value,
                                                  run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback, "message", self._state)

    def register_callback_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_callback_query_handler(callback, *custom_filters, state=self._state,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback, "callback_query", self._state)

    def register_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                      content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                       content_types=content_types, state=self._state,
                                                       run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback, "channel_post", self._state)

    def register_chosen_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_chosen_inline_handler(callback, *custom_filters, state=self._state,
                                                        run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback, "chosen_inline", self._state)

    def register_edited_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                             content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                              regexp=regexp, content_types=content_types,
                                                              state=self._state, run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback, "edited_channel_post", self._state)

    def register_edited_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                        content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                         content_types=content_types, state=self._state,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback, "edited_message", self._state)

    def register_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_inline_handler(callback, *custom_filters, state=self._state,
                                                 run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback, "inline", self._state)

    def register_pre_checkout_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_pre_checkout_query_handler(callback, *custom_filters, state=self._state,
                                                             run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback, "pre_checkout_query", self._state)

    def register_shipping_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_shipping_query_handler(callback, *custom_filters, state=self._state,
                                                         run_task=run_task, **kwargs)
        _log_registration_handler_on_state(callback, "shipping_query", self._state)


class MainRegistrar:

    def __init__(self, dispatcher: Dispatcher):

        self._dispatcher = dispatcher

    def register_fsm_handlers(self, states: Collection[AbstractState], **reg_kwargs) -> None:

        for state in states:
            registrar = Registrar(self._dispatcher, state=state)
            state_reg_kwargs = helpers.get_existing_kwargs(state.register_handlers, **reg_kwargs)
            state.register_handlers(registrar, **state_reg_kwargs)

    def register_message_handler(self, callback: Callable, states: List[AbstractState], *custom_filters, commands=None,
                                 regexp=None, content_types=None, run_task=None, **kwargs) -> None:

        reg_partial = functools.partial(self._dispatcher.register_message_handler, callback, *custom_filters,
                                        commands=commands, regexp=regexp, content_types=content_types,
                                        run_task=run_task, **kwargs)
        self._register_handler_on_states(states, reg_partial)

    def register_callback_query_handler(self, callback: Callable, states: List[AbstractState], *custom_filters,
                                        run_task=None, **kwargs) -> None:

        reg_partial = functools.partial(self._dispatcher.register_callback_query_handler, callback, *custom_filters,
                                        run_task=run_task, **kwargs)
        self._register_handler_on_states(states, reg_partial)

    def register_channel_post_handler(self, callback: Callable, states: List[AbstractState], *custom_filters,
                                      commands=None, regexp=None, content_types=None, run_task=None, **kwargs) -> None:

        reg_partial = functools.partial(self._dispatcher.register_channel_post_handler, callback, *custom_filters,
                                        commands=commands, regexp=regexp, content_types=content_types,
                                        run_task=run_task, **kwargs)
        self._register_handler_on_states(states, reg_partial)

    def register_chosen_inline_handler(self, callback: Callable, states: List[AbstractState], *custom_filters,
                                       run_task=None, **kwargs) -> None:

        reg_partial = functools.partial(self._dispatcher.register_chosen_inline_handler, callback, *custom_filters,
                                        run_task=run_task, **kwargs)
        self._register_handler_on_states(states, reg_partial)

    def register_edited_channel_post_handler(self, callback: Callable, states: List[AbstractState], *custom_filters,
                                             commands=None, regexp=None, content_types=None,
                                             run_task=None, **kwargs) -> None:

        reg_partial = functools.partial(self.register_edited_channel_post_handler, callback, *custom_filters,
                                        commands=commands, regexp=regexp, content_types=content_types,
                                        run_task=run_task, **kwargs)
        self._register_handler_on_states(states, reg_partial)

    def register_edited_message_handler(self, callback: Callable, states: List[AbstractState], *custom_filters,
                                        commands=None, regexp=None, content_types=None,
                                        run_task=None, **kwargs) -> None:

        reg_partial = functools.partial(self.register_edited_message_handler, callback, *custom_filters,
                                        commands=commands, regexp=regexp, content_types=content_types,
                                        run_task=run_task, **kwargs)
        self._register_handler_on_states(states, reg_partial)

    def register_inline_handler(self, callback: Callable, states: List[AbstractState], *custom_filters,
                                run_task=None, **kwargs) -> None:

        reg_partial = functools.partial(self._dispatcher.register_inline_handler, callback, *custom_filters,
                                        run_task=run_task, **kwargs)
        self._register_handler_on_states(states, reg_partial)

    def register_pre_checkout_query_handler(self, callback: Callable, states: List[AbstractState], *custom_filters,
                                            run_task=None, **kwargs) -> None:

        reg_partial = functools.partial(self._dispatcher.register_pre_checkout_query_handler, callback, *custom_filters,
                                        run_task=run_task, **kwargs)
        self._register_handler_on_states(states, reg_partial)

    def register_shipping_query_handler(self, callback: Callable, states: List[AbstractState], *custom_filters,
                                        run_task=None, **kwargs) -> None:

        reg_partial = functools.partial(self._dispatcher.register_shipping_query_handler, callback, *custom_filters,
                                        run_task=run_task, **kwargs)
        self._register_handler_on_states(states, reg_partial)

    def register_error_handler(self, callback: Callable, *custom_filters, exception=None,
                               run_task=None, **kwargs) -> None:

        self._dispatcher.register_errors_handler(callback, *custom_filters, exception=exception,
                                                 run_task=run_task, **kwargs)
        _log_registration_handler(callback, "error_handler")

    def register_poll_answer_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_poll_answer_handler(callback, *custom_filters, run_task=run_task, **kwargs)
        _log_registration_handler(callback, "poll_answer")

    def register_poll_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_poll_handler(callback, *custom_filters, run_task=run_task, **kwargs)
        _log_registration_handler(callback, "poll")

    @staticmethod
    def _register_handler_on_states(states: List[AbstractState], reg_partial: functools.partial) -> None:

        for state in states:
            reg_partial(state=state.name)

        handler_type = reg_partial.func.__name__.replace("register_", "", 1).replace("_handler", "", 1)
        callback_name = reg_partial.keywords["callback"].__qualname__

        logger.debug(f"Handler '{callback_name}' (type='{handler_type}') is registered on states: {states}!")
