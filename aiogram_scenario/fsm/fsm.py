import inspect
from typing import Optional, Callable, Iterable, Union
import logging

from aiogram import Dispatcher

from .state import BaseState
from .states_mapping import StatesMapping
from .storages.base import BaseStorage, Magazine
from .transitions.keeper import TransitionsKeeper
from .transitions.locking.storages.base import AbstractLockingStorage
from .transitions.locking.storages.memory import MemoryLockingStorage
from .types import RawTransitionsType
from aiogram_scenario.registrars.fsm import FSMHandlersRegistrar
from aiogram_scenario import errors


logger = logging.getLogger(__name__)


def _get_spec_kwargs(callback: Callable, kwargs: dict) -> dict:

    # try to resolve decorated callbacks
    while hasattr(callback, '__wrapped__'):
        callback = callback.__wrapped__

    spec = inspect.getfullargspec(callback)

    return {k: v for k, v in kwargs.items() if k in set(spec.args + spec.kwonlyargs)}


class FSM:

    def __init__(self, dispatcher: Dispatcher, *, locking_storage: Optional[AbstractLockingStorage] = None,
                 initial_state: Optional[BaseState] = None):

        if not isinstance(dispatcher.storage, BaseStorage):  # in case of storage from aiogram
            raise errors.InvalidFSMStorageTypeError(type(dispatcher.storage))

        self._dispatcher = dispatcher
        self._states_mapping = StatesMapping()

        self._initial_state: Optional[BaseState] = None
        if initial_state is not None:
            self.set_initial_state(initial_state)

        self._locking_storage = locking_storage or MemoryLockingStorage()
        self._transitions_keeper = TransitionsKeeper()
        self.handlers_registrar = FSMHandlersRegistrar(self._dispatcher, self._states_mapping)

    @property
    def is_initialized(self) -> bool:

        return self._initial_state is not None

    @property
    def initial_state(self) -> Optional[BaseState]:

        return self._initial_state

    @initial_state.setter
    def initial_state(self, state: BaseState) -> None:

        self.set_initial_state(state)

    @property
    def storage(self) -> BaseStorage:

        return self._dispatcher.storage

    def set_initial_state(self, state: BaseState) -> None:

        if self._initial_state is not None:
            raise errors.InitialStateIsAlreadySetError()

        self._initial_state = state
        self._states_mapping.add(None, state)

        logger.info(f"Initial state '{state}' is set!")

    async def get_current_state(self, *, chat_id: int, user_id: int) -> BaseState:

        value = await self.storage.get_state(chat=chat_id, user=user_id)
        state = self._states_mapping.get_state(value)

        return state

    def add_transition(self, source_state: BaseState, destination_state: BaseState,
                       handler: Union[str, Callable], direction: Optional[str] = None) -> None:

        if isinstance(handler, Callable):
            handler = handler.__name__

        try:
            self._check_initialization()
            self._transitions_keeper.add(source_state=source_state, destination_state=destination_state,
                                         handler=handler, direction=direction)

            for state in (source_state, destination_state):
                if not self._states_mapping.check_state(state):
                    self._states_mapping.add(state.name, state)
        except errors.BaseError as error:
            raise errors.TransitionAddingError(source_state=source_state, destination_state=destination_state,
                                               handler=handler, direction=direction) from error

        logger.info(f"Added transition (source_state='{source_state}', "
                    f"destination_state='{destination_state}', {handler=}, {direction=})!")

    def check_transition(self, source_state: BaseState, destination_state: BaseState,
                         handler: str, direction: Optional[str] = None) -> bool:

        return self._transitions_keeper.check(source_state=source_state, destination_state=destination_state,
                                              handler=handler, direction=direction)

    def remove_transition(self, source_state: BaseState, handler: Union[str, Callable],
                          direction: Optional[str] = None) -> None:

        if isinstance(handler, Callable):
            handler = handler.__name__

        try:
            destination_state = self._transitions_keeper.remove(source_state=source_state,
                                                                handler=handler, direction=direction)

            for state in (source_state, destination_state):
                if (state is not self._initial_state) and (state not in self._transitions_keeper.states):
                    self._states_mapping.remove_by_state(state)
        except errors.BaseError as error:
            raise errors.TransitionRemovingError(source_state=source_state,
                                                 handler=handler, direction=direction) from error

        logger.info(f"Removed transition (source_state='{source_state}', "
                    f"destination_state='{destination_state}', {handler=}, {direction=})!")

    def import_transitions(self, transitions: RawTransitionsType, states: Iterable[BaseState]) -> None:

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

    async def execute_transition(self, *, chat_id: int, user_id: int, destination_state: BaseState,
                                 process_exit: bool = True, processing_args: tuple = (),
                                 processing_kwargs: Optional[dict] = None) -> None:

        if destination_state not in self._transitions_keeper.states:
            raise errors.StateIsNotUsedInTransitions(destination_state)

        magazine = self.storage.get_magazine(chat=chat_id, user=user_id)
        await magazine.load()

        source_state = self._states_mapping.get_state(magazine.current_state)
        await self._process_transition_with_magazine(magazine, source_state=source_state,
                                                     destination_state=destination_state,
                                                     process_exit=process_exit,
                                                     processing_args=processing_args,
                                                     processing_kwargs=processing_kwargs)

    async def execute_next_transition(self, *, chat_id: int, user_id: int, handler: str,
                                      direction: Optional[str] = None, processing_args: tuple = (),
                                      processing_kwargs: Optional[dict] = None) -> None:

        magazine = self.storage.get_magazine(chat=chat_id, user=user_id)
        await magazine.load()

        source_state = self._states_mapping.get_state(magazine.current_state)
        try:
            destination_state = self._transitions_keeper.get_destination_state(source_state, handler, direction)
        except errors.TransitionNotFoundError as error:
            raise errors.NextTransitionNotFoundError(chat_id=chat_id, user_id=user_id) from error

        await self._process_transition_with_magazine(magazine, source_state=source_state,
                                                     destination_state=destination_state,
                                                     processing_args=processing_args,
                                                     processing_kwargs=processing_kwargs)

    async def execute_back_transition(self, *, chat_id: int, user_id: int, processing_args: tuple = (),
                                      processing_kwargs: Optional[dict] = None) -> None:

        magazine = self.storage.get_magazine(chat=chat_id, user=user_id)
        await magazine.load()

        source_state = self._states_mapping.get_state(magazine.current_state)
        try:
            destination_state = self._states_mapping.get_state(magazine.penultimate_state)
        except errors.StateValueNotFoundError as error:
            raise errors.BackTransitionNotFoundError(chat_id=chat_id, user_id=user_id) from error

        await self._process_transition_with_magazine(magazine, source_state=source_state,
                                                     destination_state=destination_state,
                                                     processing_args=processing_args,
                                                     processing_kwargs=processing_kwargs)

    async def _process_transition_with_magazine(self, magazine: Magazine, *, source_state: BaseState,
                                                destination_state: BaseState, process_exit: bool = True,
                                                processing_args: tuple = (),
                                                processing_kwargs: Optional[dict] = None) -> None:

        chat_id, user_id = magazine.chat_id, magazine.user_id

        try:
            async with self._locking_storage.acquire(chat_id=chat_id, user_id=user_id):
                logger.debug(f"Started transition from '{source_state}' to '{destination_state}' "
                             f"({chat_id=}, {user_id=})...")

                if processing_kwargs is None:
                    exit_kwargs, enter_kwargs = {}, {}
                else:
                    exit_kwargs, enter_kwargs = [_get_spec_kwargs(method, processing_kwargs)
                                                 for method in (source_state.process_exit,
                                                                destination_state.process_enter)]

                if process_exit:
                    await source_state.process_exit(*processing_args, **exit_kwargs)
                    logger.debug(f"Produced exit from state '{source_state}' ({chat_id=}, {user_id=})!")

                await destination_state.process_enter(*processing_args, **enter_kwargs)
                logger.debug(f"Produced enter to state '{destination_state}' ({chat_id=}, {user_id=})!")

                if source_state is not destination_state:
                    await magazine.push(self._states_mapping.get_value(destination_state))
                    logger.debug(f"State '{destination_state}' is set ({chat_id=}, {user_id=})!")

        except errors.TransitionLockIsActiveError:
            raise errors.TransitionIsLockedError(chat_id=chat_id, user_id=user_id,
                                                 source_state=source_state, destination_state=destination_state)

        logger.debug(f"Transition from '{source_state}' to '{destination_state}' ({chat_id=}, {user_id=}) completed!")

    def _check_initialization(self):

        if not self.is_initialized:
            raise errors.FSMIsNotInitializedError()
