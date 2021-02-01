from typing import Optional, List, Callable, Collection
import logging

from aiogram import Dispatcher

from .state import BaseState
from .states_mapping import StatesMapping
from .storages.base import BaseStorage, Magazine
from .transitions.keeper import TransitionsKeeper
from .transitions.adapters.base import AbstractTransitionsAdapter
from .transitions.locking.storages.base import AbstractLocksStorage
from .transitions.locking.storages.memory import MemoryLocksStorage
from aiogram_scenario import exceptions, helpers
from aiogram_scenario.helpers import EventUnionType
from aiogram_scenario.handlers_registrars import FSMHandlersRegistrar


logger = logging.getLogger(__name__)


class FSM:

    def __init__(self, dispatcher: Dispatcher, *, locks_storage: Optional[AbstractLocksStorage] = None,
                 initial_state: Optional[BaseState] = None):

        if not isinstance(dispatcher.storage, BaseStorage):
            raise exceptions.InvalidFSMStorageError(type(dispatcher.storage).__name__)

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
    def initial_state(self) -> Optional[BaseState]:

        return self._initial_state

    @property
    def storage(self) -> BaseStorage:

        return self._dispatcher.storage

    def set_initial_state(self, state: BaseState) -> None:

        if self._initial_state is not None:
            raise exceptions.InitialStateSettingError("initial state has already been set before!")

        self._initial_state = state
        self._check_and_register_state(state)

        logger.info(f"Initial state ({self._initial_state}) is set!")

    def unset_initial_state(self) -> None:

        if self._initial_state is None:
            raise exceptions.InitialStateUnsettingError("the initial state has not been set!")

        state, self._initial_state = self._initial_state, None
        self._check_and_unregister_state(state)

        logger.info("Initial state is unset!")

    def _check_and_register_state(self, state: BaseState):

        if self._states_mapping.states_values.get(state) is None:
            if state is self._initial_state:
                self._states_mapping[None] = state
            else:
                self._states_mapping[state.name] = state

    def _check_and_unregister_state(self, state: BaseState):

        states = self._transitions_keeper.get_states()
        if (state is not self._initial_state) and (state not in states):
            value = self._states_mapping.states_values[state]
            del self._states_mapping[value]

    def add_transition(self, source_state: BaseState, trigger: Callable,
                       destination_state: BaseState) -> None:

        self._transitions_keeper.add(source_state, trigger, destination_state)
        for state in (source_state, destination_state):
            self._check_and_register_state(state)

        logger.info(f"Added transition from '{source_state}' ('{trigger.__qualname__}') to '{destination_state}'!")

    def remove_transition(self, source_state: BaseState, trigger: Callable,
                          destination_state: BaseState) -> None:

        self._transitions_keeper.remove(source_state, trigger, destination_state)
        for state in (source_state, destination_state):
            self._check_and_unregister_state(state)

        logger.info(f"Removed transition from '{source_state}' ('{trigger.__qualname__}') to '{destination_state}'!")

    async def execute_transition(self, source_state: BaseState, destination_state: BaseState, *,
                                 event: EventUnionType, context_kwargs: dict, magazine: Magazine) -> None:

        chat_id, user_id = magazine.chat_id, magazine.user_id
        async with self._locks_storage.acquire(source_state, destination_state,
                                               chat_id=chat_id, user_id=user_id):
            logger.debug(f"Started transition from '{source_state}' to '{destination_state}' "
                         f"({chat_id=}, {user_id=})...")

            exit_kwargs, enter_kwargs = [helpers.get_existing_kwargs(method, check_varkw=True, **context_kwargs)
                                         for method in (source_state.process_exit, destination_state.process_enter)]

            await source_state.process_exit(event, **exit_kwargs)
            logger.debug(f"Produced exit from state '{source_state}' ({chat_id=}, {user_id=})!")
            await destination_state.process_enter(event, **enter_kwargs)
            logger.debug(f"Produced enter to state '{destination_state}' ({chat_id=}, {user_id=})!")
            await magazine.push(self._states_mapping.states_values[destination_state])
            logger.debug(f"State '{destination_state}' is set ({chat_id=}, {user_id=})!")

        logger.debug(f"Transition to '{destination_state}' ({chat_id=}, {user_id=}) completed!")

    def import_transitions(self, adapter: AbstractTransitionsAdapter, *,
                           states: Optional[Collection[BaseState]] = None,
                           triggers: Optional[Collection[Callable]] = None) -> None:

        if states is None:
            states = list(self._states_mapping.states_values)
        if triggers is None:
            triggers = self.registrar.get_registered_handlers()

        if not states:
            raise exceptions.TransitionsImportError("no states!")
        if not triggers:
            raise exceptions.TransitionsImportError("no triggers!")

        transitions = adapter.get_transitions()
        states_mapping = {state.name: state for state in states}
        triggers_mapping = {trigger.__name__: trigger for trigger in triggers}

        for source_state in transitions:
            for trigger, destination_state in transitions[source_state].items():
                self.add_transition(
                    source_state=states_mapping[source_state],
                    trigger=triggers_mapping[trigger],
                    destination_state=states_mapping[destination_state]
                )

        logger.info(f"Transitions from '{adapter.filename}' file successfully imported!")

    async def execute_next_transition(self, trigger: Callable, *, event: EventUnionType,
                                      context_kwargs: dict, chat_id: int, user_id: int) -> None:

        magazine = self.storage.get_magazine(chat=chat_id, user=user_id)
        await magazine.load()

        source_state = self._states_mapping.values_states[magazine.current_state]
        try:
            destination_state = self._transitions_keeper[source_state][trigger]
        except KeyError:
            raise exceptions.TransitionNotFoundError(f"not found next transition ({source_state=}, "
                                                     f"{chat_id=}, {user_id=})!")

        await self.execute_transition(
            source_state=source_state,
            destination_state=destination_state,
            event=event,
            context_kwargs=context_kwargs,
            magazine=magazine
        )

    async def execute_back_transition(self, *, event: EventUnionType, context_kwargs: dict,
                                      chat_id: int, user_id: int) -> None:

        magazine = self.storage.get_magazine(chat=chat_id, user=user_id)
        await magazine.load()

        source_state = self._states_mapping.values_states[magazine.current_state]
        try:
            destination_state = self._states_mapping.values_states[magazine.penultimate_state]
        except exceptions.StateNotFoundError:
            raise exceptions.TransitionNotFoundError(f"not found back transition ({source_state=}, "
                                                     f"{chat_id=}, {user_id=})!")

        await self.execute_transition(
            source_state=source_state,
            destination_state=destination_state,
            event=event,
            context_kwargs=context_kwargs,
            magazine=magazine
        )

    async def set_transitions_chronology(self, states: List[BaseState], *, chat_id: int, user_id: int) -> None:

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
            magazine.set(self._states_mapping.states_values[state])
        await magazine.commit()

        logger.info(f"Chronology of transitions ({', '.join(magazine.states)}) is set ({chat_id=}, {user_id=})!")
