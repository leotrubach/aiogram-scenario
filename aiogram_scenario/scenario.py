from typing import Optional
import inspect
import logging

from aiogram.dispatcher import Dispatcher

from .states_map import StatesMap
from .state import AbstractState, HandlersRegistrar


logger = logging.getLogger(__name__)


def _get_transition_args(process_obj, **context_kwargs: dict) -> dict:

    spec = inspect.getfullargspec(process_obj)
    if spec.varkw:
        return context_kwargs

    return {k: v for k, v in context_kwargs.items() if k in spec.args}


class Scenario:
    """ The scenario class allows registering target_state map handlers,
        as well as performing transitions between them.
    """

    def __init__(self, states_map: StatesMap, dispatcher: Dispatcher):

        self.states_map = states_map
        self._dispatcher = dispatcher

    async def execute_transition(self, target_state: AbstractState, user_id: Optional[int] = None,
                                 chat_id: Optional[int] = None, *handler_args, **context_kwargs: dict):
        """ Performs a state transition operation. """

        logger.debug(f"User {user_id} transitions to state {target_state!r} in chat {chat_id}...")
        if target_state not in self.states_map.states:
            raise RuntimeError(f"unknown target_state: {target_state}")

        fsm_context = self._dispatcher.current_state(chat=chat_id, user=user_id)

        await fsm_context.set_state(target_state.name)

        context_kwargs = _get_transition_args(target_state.process_transition, **context_kwargs)
        await target_state.process_transition(*handler_args, **context_kwargs)

    def register_handlers(self):
        """ Registers all states map handlers. """

        logger.debug("Handlers registration started...")
        for state in self.states_map.states:
            registrar = HandlersRegistrar(self._dispatcher, state=state)
            state.register_handlers(registrar)
