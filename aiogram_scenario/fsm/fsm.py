from typing import Optional, Union, List, Callable, Collection, Dict
import logging

from .state import BaseState
from .storages.base import BaseStorage, Magazine
from .transitions.keeper import TransitionsKeeper
from .transitions.adapters import AbstractTransitionsAdapter
from .transitions.locking.storages import AbstractLocksStorage, MemoryLocksStorage
from aiogram_scenario import exceptions, helpers
from aiogram_scenario.helpers import EventUnionType


logger = logging.getLogger(__name__)


class FSM:

    def __init__(self, storage: BaseStorage, *, locks_storage: Optional[AbstractLocksStorage] = None,
                 initial_state: Optional[BaseState] = None):

        if not isinstance(storage, BaseStorage):
            raise exceptions.InvalidFSMStorageError(type(storage).__name__)

        self._storage = storage

        self._initial_state: Optional[BaseState] = None
        if initial_state is not None:
            self.set_initial_state(initial_state)

        if locks_storage is None:
            locks_storage = MemoryLocksStorage()
        self._locks_storage = locks_storage

        self._transitions_keeper = TransitionsKeeper()
        self._states_mapping: Dict[Union[None, str], BaseState] = {}

    def __del__(self):

        if self._initial_state is not None:
            self.unset_initial_state()

        for source_state in self._transitions_keeper:
            for trigger, destination_state in self._transitions_keeper[source_state]:
                self.remove_transition(source_state, trigger, destination_state)

    def set_initial_state(self, state: BaseState) -> None:

        if self._initial_state is not None:
            raise exceptions.InitialStateSettingError("initial state has already been set before!")
        elif state.fsm is not None:
            raise exceptions.InitialStateSettingError(f"state '{state}' is used in another FSM!")

        state.value = None  # taken from aiogram
        state.is_initial = True
        self._initial_state = state
        self._initial_state.fsm = self

        logger.info(f"Initial state ({self._initial_state}) is set!")

    def unset_initial_state(self) -> None:

        if self._initial_state is None:
            raise exceptions.InitialStateUnsettingError("the initial state has not been set!")

        self._initial_state.value = self._initial_state.name
        self._initial_state.fsm = None

        logger.info("Initial state is unset!")

    def add_transition(self, source_state: BaseState, trigger: Callable,
                       destination_state: BaseState) -> None:

        for state in (source_state, destination_state):
            if all(state.fsm is not i for i in (None, self)):
                raise exceptions.TransitionAddingError(f"state '{state}' is used in another FSM!")

            if state.fsm is None:
                state.is_initial = False
                state.fsm = self

            if self._states_mapping.get(state.value) is None:
                self._states_mapping[state.value] = state

        self._transitions_keeper.add(source_state, trigger, destination_state)

        logger.info(f"Added transition from '{source_state}' ('{trigger.__qualname__}') to '{destination_state}'!")

    def remove_transition(self, source_state: BaseState, trigger: Callable,
                          destination_state: BaseState) -> None:

        for state in (source_state, destination_state):
            if state.fsm is not self:
                raise exceptions.TransitionRemovingError(f"state '{state}' is unused in this FSM!")

        self._transitions_keeper.remove(source_state, trigger, destination_state)
        states = self._transitions_keeper.get_states()
        for state in (source_state, destination_state):
            if (state is not self._initial_state) and (state not in states):
                state.fsm = None

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
            await magazine.push(destination_state.value)
            logger.debug(f"State '{destination_state}' is set ({chat_id=}, {user_id=})!")

        logger.debug(f"Transition to '{destination_state}' ({chat_id=}, {user_id=}) completed!")

    def import_transitions(self, adapter: AbstractTransitionsAdapter, *,
                           states: Collection[BaseState],
                           triggers: Collection[Callable]) -> None:

        if not states:
            raise exceptions.TransitionsImportError("no states!")
        if not triggers:
            raise exceptions.TransitionsImportError("no triggers!")

        transitions = adapter.get_transitions()
        states_mapping = {str(state): state for state in states}
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

        magazine = self._storage.get_magazine(chat=chat_id, user=user_id)
        await magazine.load()

        source_state = self._states_mapping[magazine.current_state]
        try:
            destination_state = self._transitions_keeper[source_state][trigger]
        except KeyError:
            raise exceptions.NextTransitionNotFoundError(
                source_state=str(source_state),
                chat_id=chat_id,
                user_id=user_id
            )

        await self.execute_transition(
            source_state=source_state,
            destination_state=destination_state,
            event=event,
            context_kwargs=context_kwargs,
            magazine=magazine
        )

    async def execute_back_transition(self, *, event: EventUnionType, context_kwargs: dict,
                                      chat_id: int, user_id: int) -> None:

        magazine = self._storage.get_magazine(chat=chat_id, user=user_id)
        await magazine.load()

        source_state = self._states_mapping[magazine.current_state]
        try:
            destination_state = self._states_mapping[magazine.penultimate_state]
        except exceptions.StateNotFoundError:
            raise exceptions.NextTransitionNotFoundError(
                source_state=magazine.current_state,
                chat_id=chat_id,
                user_id=user_id
            )

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

        magazine = self._storage.get_magazine(chat=chat_id, user=user_id)
        for state in states:
            magazine.set(state.value)
        await magazine.commit()

        logger.info(f"Chronology of transitions ({', '.join(magazine.states)}) is set ({chat_id=}, {user_id=})!")
