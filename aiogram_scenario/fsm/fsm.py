import inspect
from typing import Optional, List, Collection, Callable
import logging

from aiogram import Dispatcher

from .state import BaseState
from .states_mapping import StatesMapping
from .storages.base import BaseStorage, Magazine
from .transitions.keeper import TransitionsKeeper
from .transitions.locking.storages.base import AbstractLocksStorage
from .transitions.locking.storages.memory import MemoryLocksStorage
from .types import RawTransitionsType
from aiogram_scenario import exceptions, helpers
from aiogram_scenario.registrars.fsm import FSMHandlersRegistrar


logger = logging.getLogger(__name__)


def _get_spec_kwargs(callback: Callable, kwargs: dict) -> dict:

    spec = inspect.getfullargspec(callback)
    if spec.varkw:
        return kwargs

    return {k: v for k, v in kwargs.items() if k in set(spec.args + spec.kwonlyargs)}


class FSM:

    def __init__(self, dispatcher: Dispatcher, *, locks_storage: Optional[AbstractLocksStorage] = None,
                 initial_state: Optional[BaseState] = None):

        if not isinstance(dispatcher.storage, BaseStorage):
            raise TypeError(f"invalid storage type '{type(dispatcher.storage).__name__}'! "
                            "Select a storage from aiogram_scenario.fsm.storages!")

        self._dispatcher = dispatcher

        self._initial_state: Optional[BaseState] = None
        if initial_state is not None:
            self.set_initial_state(initial_state)

        if locks_storage is None:
            locks_storage = MemoryLocksStorage()
        self._locks_storage = locks_storage

        self._transitions_keeper = TransitionsKeeper()
        self._states_mapping = StatesMapping()
        self.registrar = FSMHandlersRegistrar(self._dispatcher, self._states_mapping)

    @property
    def is_initialized(self) -> bool:

        return self._initial_state is not None

    @property
    def initial_state(self) -> Optional[BaseState]:

        return self._initial_state

    @property
    def storage(self) -> BaseStorage:

        return self._dispatcher.storage

    def set_initial_state(self, state: BaseState) -> None:

        if self._initial_state is not None:
            raise exceptions.InitialStateSettingError("initial state has already been set before!")

        self._initial_state = state
        self._states_mapping[None] = state

        logger.info(f"Initial state '{state}' is set!")

    def unset_initial_state(self) -> None:

        if self._initial_state is None:
            raise exceptions.InitialStateUnsettingError("initial state is not set!")

        self._initial_state = None
        del self._states_mapping[None]

        logger.info(f"Initial state is unset!")

    def add_transition(self, source_state: BaseState, destination_state: BaseState,
                       handler: str, direction: Optional[str] = None) -> None:

        if not self.is_initialized:
            raise exceptions.FSMIsNotInitialized()

        self._transitions_keeper.add(source_state, destination_state, handler, direction)
        for state in (source_state, destination_state):
            if not self._states_mapping.check_existence(state):
                self._states_mapping[state.name] = state

        logger.info(f"Added transition ({source_state=}, {destination_state=}, {handler=}, {direction=})!")

    def remove_transition(self, source_state: BaseState, destination_state: BaseState,
                          handler: str, direction: Optional[str] = None) -> None:

        if not self.is_initialized:
            raise exceptions.FSMIsNotInitialized()

        self._transitions_keeper.remove(source_state, destination_state, handler, direction)
        states = self._transitions_keeper.get_states()
        for state in (source_state, destination_state):
            if (state != self._initial_state) and (state not in states):
                del self._states_mapping[state]

        logger.info(f"Removed transition ({source_state=}, {destination_state=}, {handler=}, {direction=})!")

    async def execute_transition(self, source_state: BaseState, destination_state: BaseState, *,
                                 magazine: Magazine, processing_args: tuple, processing_kwargs: dict) -> None:

        if not magazine.is_loaded:
            await magazine.load()

        chat_id, user_id = magazine.chat_id, magazine.user_id
        async with self._locks_storage.acquire(source_state, destination_state,
                                               chat_id=chat_id, user_id=user_id):
            logger.debug(f"Started transition from '{source_state}' to '{destination_state}' "
                         f"({chat_id=}, {user_id=})...")

            exit_kwargs, enter_kwargs = [_get_spec_kwargs(method, processing_kwargs)
                                         for method in (source_state.process_exit, destination_state.process_enter)]

            await source_state.process_exit(*processing_args, **exit_kwargs)
            logger.debug(f"Produced exit from state '{source_state}' ({chat_id=}, {user_id=})!")
            await destination_state.process_enter(*processing_args, **enter_kwargs)
            logger.debug(f"Produced enter to state '{destination_state}' ({chat_id=}, {user_id=})!")
            await magazine.push(self._states_mapping.get_value(destination_state))
            logger.debug(f"State '{destination_state}' is set ({chat_id=}, {user_id=})!")

        logger.debug(f"Transition to '{destination_state}' ({chat_id=}, {user_id=}) completed!")

    def import_transitions(self, transitions: RawTransitionsType, *, states: Collection[BaseState]) -> None:

        states_mapping = {state.name: state for state in states}
        for source_state in transitions:
            for handler in transitions[source_state]:
                for direction, destination_state in transitions[source_state][handler].items():
                    self.add_transition(
                        source_state=states_mapping[source_state],
                        destination_state=states_mapping[destination_state],
                        handler=handler,
                        direction=direction
                    )

        logger.info(f"Transitions successfully imported!")

    async def execute_next_transition(self, handler: str, direction: Optional[str] = None, *,
                                      magazine: Magazine, processing_args: tuple,
                                      processing_kwargs: dict) -> None:

        if not magazine.is_loaded:
            await magazine.load()

        source_state = self._states_mapping.get_state(magazine.current_state)
        try:
            destination_state = self._transitions_keeper[source_state][handler][direction]
        except KeyError:
            chat_id, user_id = magazine.chat_id, magazine.user_id
            raise exceptions.TransitionNotFoundError(f"not found next transition ({source_state=}, "
                                                     f"{handler=}, {direction=} {chat_id=}, {user_id=})!")

        await self.execute_transition(source_state, destination_state, magazine=magazine,
                                      processing_args=processing_args, processing_kwargs=processing_kwargs)

    async def execute_back_transition(self, *, magazine: Magazine, processing_args: tuple,
                                      processing_kwargs: dict) -> None:

        if not magazine.is_loaded:
            await magazine.load()

        source_state = self._states_mapping.get_state(magazine.current_state)
        try:
            destination_state = self._states_mapping.get_state(magazine.penultimate_state)
        except exceptions.StateNotFoundError:
            chat_id, user_id = magazine.chat_id, magazine.user_id
            raise exceptions.TransitionNotFoundError(f"not found back transition ({source_state=}, "
                                                     f"{chat_id=}, {user_id=})!")

        await self.execute_transition(source_state, destination_state, magazine=magazine,
                                      processing_args=processing_args, processing_kwargs=processing_kwargs)

    async def set_transitions_chronology(self, states: List[BaseState], *, chat_id: int, user_id: int) -> None:

        if not self.is_initialized:
            raise exceptions.FSMIsNotInitialized()

        for index, source_state in enumerate(states):
            try:
                destination_state = states[index + 1]
            except IndexError:
                break
            if destination_state not in self._transitions_keeper[source_state].values():
                raise exceptions.TransitionsChronologyError(
                    source_state=str(source_state),
                    destination_state=str(destination_state),
                    states=[str(i) for i in states]
                )

        magazine = self.storage.get_magazine(chat=chat_id, user=user_id)
        for state in states:
            magazine.set(self._states_mapping.get_value(state))
        await magazine.commit()

        logger.info(f"Chronology of transitions ({', '.join(magazine.states)}) is set ({chat_id=}, {user_id=})!")
