from typing import Callable
import inspect
from inspect import FullArgSpec

from aiogram.dispatcher import Dispatcher, FSMContext

from .states_map import StatesMap
from .state import HandlersRegistrar


def _get_partial_data(spec: FullArgSpec, kwargs: dict):

    if spec.varkw:
        return kwargs

    return {k: v for k, v in kwargs.items() if k in spec.args}


class Scenario:
    """ The scenario class allows registering state map handlers,
        as well as performing transitions between them.
    """

    def __init__(self, states_map: StatesMap):

        self._states_map = states_map
        self._handlers_is_registered = False

    def register_handlers(self, dispatcher: Dispatcher):
        """ Registers all states map handlers. """

        if not self._handlers_is_registered:
            for state in self._states_map.states:
                registrar = HandlersRegistrar(dispatcher, state=state)
                state.register_handlers(registrar)
            self._handlers_is_registered = True
        else:
            raise RuntimeError("handlers are already registered!")

    def check_target_state_existence(self, pointing_handler: Callable) -> bool:
        """ Checks the target state for existence. """

        target_state = self._states_map.get_target_state(pointing_handler)
        return target_state is not None

    async def execute_transition(self, pointing_handler: Callable, fsm_context: FSMContext, *args, context_data: dict):
        """ Executes transition to the next state. """

        target_state = self._states_map.get_target_state(pointing_handler)

        await fsm_context.set_state(target_state.name)
        await self._run_transition_process(target_state.process_transition, *args, context_data=context_data)

    @staticmethod
    async def _run_transition_process(process: Callable, *args, context_data: dict):
        """ Moves to the next state, given the signature (low-level method). """

        process_spec = inspect.getfullargspec(process)
        partial_data = _get_partial_data(process_spec, context_data)
        await process(*args, **partial_data)

    @property
    def handlers_is_registered(self):

        return self._handlers_is_registered
