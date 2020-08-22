from typing import Optional, List, Callable, Collection
from dataclasses import dataclass
import logging

from aiogram import Dispatcher
from aiogram.dispatcher.storage import BaseStorage

from .state import AbstractState, get_state_value
from .magazine import Magazine
from aiogram_scenario import exceptions, helpers


logger = logging.getLogger(__name__)


@dataclass()
class StateRoute:

    state: AbstractState
    pointing_handlers: Collection[Callable]


class FiniteStateMachine:

    def __init__(self, dispatcher: Dispatcher, storage: BaseStorage,
                 magazine_key: str = "fsm_states_magazine"):

        self._dispatcher = dispatcher
        self._storage = storage
        self._magazine_key = magazine_key
        self._initial_state: Optional[AbstractState] = None
        self._states_routes: List[StateRoute] = []

    @property
    def initial_state(self) -> AbstractState:

        if self._initial_state is None:
            raise exceptions.InitialStateError("initial state not set!")

        return self._initial_state

    @property
    def states(self) -> List[AbstractState]:

        try:
            states = [self.initial_state]
        except exceptions.InitialStateError:
            states = []
        states.extend([i.state for i in self._states_routes])

        return states

    def set_initial_state(self, state: AbstractState) -> None:

        if self._initial_state is not None:
            raise RuntimeError("initial state has already been set before!")
        elif not state.is_initial:
            raise exceptions.InitialStateError(f"state not indicated as initial ({state.is_initial=})!")
        elif state in self.states:
            raise exceptions.DuplicateError(f"state '{state}' is already exists!")

        self._initial_state = state

        logger.debug(f"Added initial state for FSM: '{self._initial_state}'")

    def add_state(self, state: AbstractState, pointing_handlers: Collection[Callable]) -> None:

        if state.is_initial:
            raise exceptions.StateError(f"state is indicated as initial ({state.is_initial=})!")
        elif state in self.states:
            raise exceptions.DuplicateError(f"state '{state}' is already exists!")
        elif len(set(pointing_handlers)) != len(pointing_handlers):
            raise ValueError("there are repetitions in pointing handlers!")

        existing_pointing_handlers = self._existing_pointing_handlers
        for i in pointing_handlers:
            if i in existing_pointing_handlers:
                raise exceptions.DuplicateError(f"handler '{i.__qualname__}' has already been added earlier!")

        state_route = StateRoute(state, pointing_handlers)
        self._states_routes.append(state_route)

        logger.debug(f"Added state to FSM: '{state}'")

    async def execute_transition(self, current_state: AbstractState,
                                 target_state: AbstractState,
                                 proc_args: tuple,
                                 context_kwargs: dict,
                                 user_id: Optional[int] = None,
                                 chat_id: Optional[int] = None) -> None:

        logger.debug(f"Started transition from '{current_state}' to '{target_state}' "
                     f"for '{user_id=}' in '{chat_id=}'...")

        exit_kwargs = helpers.get_existing_kwargs(current_state.process_exit, check_varkw=True, **context_kwargs)
        enter_kwargs = helpers.get_existing_kwargs(target_state.process_enter, check_varkw=True, **context_kwargs)

        await current_state.process_exit(*proc_args, **exit_kwargs)
        await target_state.process_enter(*proc_args, **enter_kwargs)

        await self._set_state(target_state, user_id=user_id, chat_id=chat_id)

        logger.debug(f"Transition to '{target_state}' for '{user_id=}' in '{chat_id=}' completed!")

    async def execute_next_transition(self, pointing_handler: Callable,
                                      event,
                                      context_kwargs: dict,
                                      user_id: Optional[int] = None,
                                      chat_id: Optional[int] = None) -> None:

        magazine = await self.get_magazine(user_id, chat_id)
        try:
            await magazine.load()
        except exceptions.MagazineInitializationError:
            await magazine.initialize(str(self.initial_state))

        current_state = self._get_state_by_name(magazine.current_state)
        target_state = self._get_state_by_pointing_handler(pointing_handler)

        await self.execute_transition(
            current_state=current_state,
            target_state=target_state,
            proc_args=(event,),
            context_kwargs=context_kwargs,
            user_id=user_id,
            chat_id=chat_id
        )

        magazine.set(str(target_state))
        await magazine.commit()

    async def execute_back_transition(self, event,
                                      context_kwargs: dict,
                                      user_id: Optional[int] = None,
                                      chat_id: Optional[int] = None) -> None:

        magazine = await self.get_magazine(user_id, chat_id)
        await magazine.load()

        penultimate_state = magazine.penultimate_state
        if penultimate_state is None:
            raise exceptions.TransitionError("there are not enough states in the magazine to return!")

        current_state = self._get_state_by_name(magazine.current_state)
        target_state = self._get_state_by_name(penultimate_state)

        await self.execute_transition(
            current_state=current_state,
            target_state=target_state,
            proc_args=(event,),
            context_kwargs=context_kwargs,
            user_id=user_id,
            chat_id=chat_id
        )

        magazine.pop()
        await magazine.commit()

    async def get_magazine(self, user_id: Optional[int] = None, chat_id: Optional[int] = None) -> Magazine:

        return Magazine(storage=self._storage, data_key=self._magazine_key,
                        user_id=user_id, chat_id=chat_id)

    async def _set_state(self, state: AbstractState,
                         user_id: Optional[int] = None,
                         chat_id: Optional[int] = None) -> None:

        fsm_context = self._dispatcher.current_state(chat=chat_id, user=user_id)
        state_value = get_state_value(state)
        await fsm_context.set_state(state_value)

    def _get_state_by_pointing_handler(self, pointing_handler: Callable) -> AbstractState:

        for route in self._states_routes:
            if pointing_handler in route.pointing_handlers:
                return route.state

        raise exceptions.StateNotFoundError(f"no target state found for '{pointing_handler.__qualname__}' handler!")

    def _get_state_by_name(self, name: str) -> AbstractState:

        for state in self.states:
            if name == state.name:
                return state

        raise exceptions.StateNotFoundError(f"no state found for '{name}' name!")

    @property
    def _existing_pointing_handlers(self) -> List[Callable]:

        handlers = []
        for i in self._states_routes:
            handlers.extend(i.pointing_handlers)

        return handlers
