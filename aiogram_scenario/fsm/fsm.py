from typing import Optional, List, Callable, Collection, Dict, Set
import logging

from .state import AbstractState
from aiogram_scenario import exceptions, helpers
from aiogram_scenario.helpers import EVENT_UNION_TYPE
from aiogram_scenario.fsm.storages.base import BaseStorage, Magazine
from aiogram_scenario.fsm.transitions.locking import TransitionsLocksStorage
from aiogram_scenario.transitions_storages.base import AbstractTransitionsStorage
from aiogram_scenario.fsm.transitions.keeper import TransitionsKeeper


logger = logging.getLogger(__name__)


class FiniteStateMachine:

    def __init__(self, storage: BaseStorage, *, initial_state: Optional[AbstractState] = None):

        if not isinstance(storage, BaseStorage):
            raise exceptions.fsm.InvalidFSMStorage("invalid storage type! Try to choose from the ones "
                                                   "suggested here: aiogram_scenario.fsm.storages")

        self._storage = storage
        self._initial_state = initial_state
        self._locks_storage = TransitionsLocksStorage()
        self._transitions_keeper = TransitionsKeeper()
        self._states_mapping: Dict[Optional[str], AbstractState] = {}

    @property
    def initial_state(self) -> AbstractState:

        if self._initial_state is None:
            raise exceptions.state.InitialStateError("initial state not set!")

        return self._initial_state

    @property
    def states(self) -> Set[AbstractState]:

        return self._transitions_keeper.states

    def set_initial_state(self, state: AbstractState) -> None:

        if self._initial_state is not None:
            raise exceptions.state.InitialStateError("initial state has already been set before!")
        elif not state.is_initial:
            raise exceptions.state.InitialStateError(f"state '{state}' not indicated "
                                                     f"as initial ({state.is_initial=})!")

        self._initial_state = state

        logger.debug(f"Added initial state for FSM: '{self._initial_state}'")

    def add_transition(self, source_state: AbstractState,
                       trigger_func: Callable,
                       destination_state: AbstractState) -> None:

        for state in (source_state, destination_state):
            if state.is_initial and (state is not self.initial_state):
                raise exceptions.fsm.TransitionAddingError(
                    f"source state '{source_state}' is defined as initial state, but it is different "
                    f"from the set initial state of the machine ('{self.initial_state}')!"
                )
            if self._states_mapping.get(state.raw_value) is None:
                self._states_mapping[state.raw_value] = state

        self._transitions_keeper.add_transition(source_state, trigger_func, destination_state)

    def remove_transition(self, source_state: AbstractState,
                          trigger_func: Callable,
                          destination_state: AbstractState) -> None:

        # TODO: Add validation checks
        self._transitions_keeper.remove_transition(source_state, trigger_func, destination_state)

    def add_transitions(self, source_states: Collection[AbstractState],
                        trigger_func: Callable,
                        destination_state: AbstractState) -> None:

        for source_state in source_states:
            self.add_transition(source_state, trigger_func, destination_state)

    async def execute_transition(self, source_state: AbstractState,
                                 destination_state: AbstractState, *,
                                 event: EVENT_UNION_TYPE,
                                 context_kwargs: dict,
                                 magazine: Optional[Magazine] = None,
                                 user_id: Optional[int] = None,
                                 chat_id: Optional[int] = None) -> None:

        if magazine is not None:
            if not magazine.is_loaded:
                raise exceptions.transition.TransitionError("magazine is not loaded!")
        else:
            magazine = self._storage.get_magazine(chat=chat_id, user=user_id)
            await magazine.load()

        with self._locks_storage.acquire(source_state, destination_state, user_id=user_id, chat_id=chat_id):
            logger.debug(f"Started transition from '{source_state}' to '{destination_state}' "
                         f"for '{user_id=}' in '{chat_id=}'...")

            exit_kwargs, enter_kwargs = [helpers.get_existing_kwargs(method, check_varkw=True, **context_kwargs)
                                         for method in (source_state.process_exit, destination_state.process_enter)]

            await source_state.process_exit(event, **exit_kwargs)
            logger.debug(f"Produced exit from state '{source_state}' for '{user_id=}' in '{chat_id=}'")
            await destination_state.process_enter(event, **enter_kwargs)
            logger.debug(f"Produced enter to state '{destination_state}' for '{user_id=}' in '{chat_id=}'")
            await magazine.push(destination_state.raw_value)
            logger.debug(f"State '{destination_state}' is set for '{user_id=}' in '{chat_id=}'")

        logger.debug(f"Transition to '{destination_state}' for '{user_id=}' in '{chat_id=}' completed!")

    def import_transitions(self, storage: AbstractTransitionsStorage, *,
                           states: Collection[AbstractState],
                           triggers_funcs: Collection[Callable]) -> None:

        if not states:
            raise exceptions.fsm.ImportTransitionsError("no states!")
        if not triggers_funcs:
            raise exceptions.fsm.ImportTransitionsError("no triggers funcs!")

        transitions = storage.read()
        states_mapping = {str(state): state for state in states}
        triggers_funcs_mapping = {trigger.__name__: trigger for trigger in triggers_funcs}

        for source_state in transitions.keys():
            for trigger_func in transitions[source_state].keys():
                destination_state = transitions[source_state][trigger_func]
                self.add_transition(
                    source_state=states_mapping[source_state],
                    trigger_func=triggers_funcs_mapping[trigger_func],
                    destination_state=states_mapping[destination_state]
                )

    def export_transitions(self, storage: AbstractTransitionsStorage) -> None:

        serialized_transitions = self._transitions_keeper.serialized_transitions
        if not serialized_transitions:
            raise exceptions.fsm.ExportTransitionsError("no transitions for export!")

        storage.write(serialized_transitions)

    async def execute_next_transition(self, trigger_func: Callable, *,
                                      event: EVENT_UNION_TYPE,
                                      context_kwargs: dict,
                                      user_id: Optional[int] = None,
                                      chat_id: Optional[int] = None) -> None:

        magazine = self._storage.get_magazine(chat=chat_id, user=user_id)
        await magazine.load()

        source_state = self._states_mapping[magazine.current_state]
        try:
            destination_state = self._transitions_keeper[source_state][trigger_func]
        except KeyError:
            raise exceptions.transition.TransitionError(f"no next transition are defined for '{source_state}' state!")

        await self.execute_transition(
            source_state=source_state,
            destination_state=destination_state,
            event=event,
            context_kwargs=context_kwargs,
            magazine=magazine,
            user_id=user_id,
            chat_id=chat_id
        )

    async def execute_back_transition(self, *, event: EVENT_UNION_TYPE,
                                      context_kwargs: dict,
                                      user_id: Optional[int] = None,
                                      chat_id: Optional[int] = None) -> None:

        magazine = self._storage.get_magazine(chat=chat_id, user=user_id)
        await magazine.load()

        try:
            penultimate_state = magazine.penultimate_state
        except exceptions.state.StateNotFoundError:
            raise exceptions.transition.TransitionError("there are not enough states in the "
                                                        f"magazine to return ({user_id=}, {chat_id=})!")

        source_state = self._states_mapping[magazine.current_state]
        destination_state = self._states_mapping[penultimate_state]

        await self.execute_transition(
            source_state=source_state,
            destination_state=destination_state,
            event=event,
            context_kwargs=context_kwargs,
            magazine=magazine,
            user_id=user_id,
            chat_id=chat_id
        )

    async def set_transitions_chronology(self, states: List[AbstractState], *,
                                         user_id: Optional[int] = None,
                                         chat_id: Optional[int] = None,
                                         check: bool = True) -> None:

        if check:
            for i in range(len(states)):
                if i == (len(states) - 1):
                    break
                source_state = states[i]
                destination_state = states[i + 1]
                if destination_state not in self._transitions_keeper[source_state].values():
                    raise exceptions.fsm.TransitionsChronologyError(f"from '{source_state}' state it is impossible "
                                                                    f"to get into '{destination_state}' state!")

        magazine = self._storage.get_magazine(chat=chat_id, user=user_id)
        for state in states:
            magazine.set(state.raw_value)
        await magazine.commit()

        logger.debug(f"Chronology of transitions set for ({user_id=}, {chat_id=})")
