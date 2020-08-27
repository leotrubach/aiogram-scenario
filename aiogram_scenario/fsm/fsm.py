from typing import Optional, List, Callable, Collection, Dict
import logging
import csv

from aiogram import Dispatcher

from .state import AbstractState
from .magazine import Magazine
from .locking import TransitionsLocksStorage
from aiogram_scenario import exceptions, helpers
from aiogram_scenario.fsm.storages import BaseStorage


logger = logging.getLogger(__name__)


class FiniteStateMachine:

    def __init__(self, dispatcher: Dispatcher, storage: BaseStorage):

        self._dispatcher = dispatcher
        self._storage = storage
        self._locks_storage = TransitionsLocksStorage()
        self._initial_state: Optional[AbstractState] = None
        self._transitions: Dict[AbstractState, Dict[Callable, AbstractState]] = {}
        self._states_mapping: Dict[str, AbstractState] = {}

    @property
    def initial_state(self) -> AbstractState:

        if self._initial_state is None:
            raise exceptions.InitialStateError("initial state not set!")

        return self._initial_state

    @property
    def source_states(self) -> List[AbstractState]:

        return list(self._transitions.keys())

    def set_initial_state(self, state: AbstractState) -> None:

        if self._initial_state is not None:
            raise exceptions.SettingInitialStateError("initial state has already been set before!")
        elif not state.is_initial:
            raise exceptions.SettingInitialStateError(f"state '{state}' not indicated "
                                                      f"as initial ({state.is_initial=})!")

        self._initial_state = state

        logger.debug(f"Added initial state for FSM: '{self._initial_state}'")

    def add_transition(self, source_state: AbstractState,
                       signal_handler: Callable,
                       destination_state: AbstractState) -> None:

        if source_state == destination_state:
            raise exceptions.AddingTransitionError(f"source state '{source_state}' is the same as destination state!")
        elif self._transitions.get(source_state) is None:

            if source_state.is_initial:
                if any(i.is_initial for i in self.source_states):
                    raise exceptions.AddingTransitionError("initial state has already been added earlier! "
                                                           f"Source state '{source_state}' is indicated as initial!")
            self._transitions[source_state] = {}
            self._states_mapping[str(source_state)] = source_state
        elif self._transitions[source_state].get(signal_handler) is not None:
            raise exceptions.AddingTransitionError("transition for the signal handler "
                                                   f"'{signal_handler.__qualname__}' is already defined "
                                                   f"in '{source_state}' state!")

        self._transitions[source_state][signal_handler] = destination_state

        logger.debug(f"Added transition from '{source_state}' "
                     f"('{signal_handler.__qualname__}') to '{destination_state}'")

    def add_transitions(self, source_states: Collection[AbstractState],
                        signal_handler: Callable,
                        destination_state: AbstractState) -> None:

        for source_state in source_states:
            self.add_transition(source_state, signal_handler, destination_state)

    async def execute_transition(self, source_state: AbstractState,
                                 destination_state: AbstractState,
                                 event,
                                 context_kwargs: dict,
                                 magazine: Magazine,
                                 user_id: Optional[int] = None,
                                 chat_id: Optional[int] = None) -> None:

        if not magazine.is_loaded:
            raise exceptions.TransitionError("magazine is not loaded!")

        with self._locks_storage.acquire(source_state, destination_state, user_id, chat_id):
            logger.debug(f"Started transition from '{source_state}' to '{destination_state}' "
                         f"for '{user_id=}' in '{chat_id=}'...")

            exit_kwargs, enter_kwargs = [helpers.get_existing_kwargs(method, check_varkw=True, **context_kwargs)
                                         for method in (source_state.process_exit, destination_state.process_enter)]

            await source_state.process_exit(event, **exit_kwargs)
            logger.debug(f"Produced exit from state '{source_state}' for '{user_id=}' in '{chat_id=}'")
            await destination_state.process_enter(event, **enter_kwargs)
            logger.debug(f"Produced enter to state '{destination_state}' for '{user_id=}' in '{chat_id=}'")

            await self._set_state(destination_state, user_id=user_id, chat_id=chat_id)

            magazine.set(str(destination_state))
            await magazine.commit()

        logger.debug(f"Transition to '{destination_state}' for '{user_id=}' in '{chat_id=}' completed!")

    def import_transitions_from_csv(self, filename: str,
                                    states: Collection[AbstractState],
                                    signal_handlers: Collection[Callable], *,
                                    encoding: str = "UTF-8",
                                    empty_cell: str = "",
                                    join_state: bool = True) -> None:

        if not states:
            raise exceptions.ImportTransitionsFromCSVError("no states!")
        if not signal_handlers:
            raise exceptions.ImportTransitionsFromCSVError("no signal handlers!")

        with open(filename, encoding=encoding, newline="") as csv_fp:
            reader = csv.reader(csv_fp)
            rows = list(reader)

        if join_state:
            for row in rows:
                for index, cell in enumerate(row[1:], start=1):
                    if (cell != empty_cell) and (not cell.endswith("State")):
                        row[index] = cell + "State"

        source_states = rows[0][1:]

        states_mapping = {str(state): state for state in states}
        signal_handlers_mapping = {handler.__name__: handler for handler in signal_handlers}

        for row in rows[1:]:
            signal_handler = row[0]
            for index, destination_state in enumerate(row[1:]):
                if destination_state != empty_cell:
                    source_state = source_states[index]
                    self.add_transition(
                        source_state=states_mapping[source_state],
                        signal_handler=signal_handlers_mapping[signal_handler],
                        destination_state=states_mapping[destination_state]
                    )

    def export_transitions_to_csv(self, filename: str, *,
                                  encoding: str = "UTF-8",
                                  empty_cell: str = "",
                                  cut_state: bool = True) -> None:

        if not self._transitions:
            raise exceptions.ExportTransitionsToCSVError("no transitions set for export!")

        rows = [["", *self._states_mapping.keys()]]
        source_states = self.source_states
        signal_handlers = self._signal_handlers

        for signal_handler in signal_handlers:
            destination_states = []
            for source_state in source_states:
                destination_state = self._transitions[source_state].get(signal_handler)
                if destination_state is None:
                    destination_state = empty_cell
                else:
                    destination_state = str(destination_state)
                destination_states.append(destination_state)
            rows.append([signal_handler.__name__, *destination_states])

        if cut_state:
            for row in rows:
                for index, cell in enumerate(row[1:], start=1):
                    if (cell != empty_cell) and (cell.endswith("State")):
                        row[index] = cell[:-5]

        with open(filename, "w", encoding=encoding, newline="") as csv_fp:
            writer = csv.writer(csv_fp)
            writer.writerows(rows)

    async def execute_next_transition(self, signal_handler: Callable,
                                      event,
                                      context_kwargs: dict,
                                      user_id: Optional[int] = None,
                                      chat_id: Optional[int] = None) -> None:

        magazine = self.get_magazine(user_id, chat_id)
        try:
            await magazine.load()
        except exceptions.MagazineInitializationError:
            await magazine.initialize(str(self.initial_state))

        source_state = self._states_mapping[magazine.current_state]
        destination_state = self._transitions[source_state][signal_handler]

        await self.execute_transition(
            source_state=source_state,
            destination_state=destination_state,
            event=event,
            context_kwargs=context_kwargs,
            magazine=magazine,
            user_id=user_id,
            chat_id=chat_id
        )

    async def execute_back_transition(self, event,
                                      context_kwargs: dict,
                                      user_id: Optional[int] = None,
                                      chat_id: Optional[int] = None) -> None:

        magazine = self.get_magazine(user_id, chat_id)
        await magazine.load()

        penultimate_state = magazine.penultimate_state
        if penultimate_state is None:
            raise exceptions.TransitionError("there are not enough states in the magazine to return!")

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

    async def set_transitions_chronology(self, states: List[AbstractState],
                                         user_id: Optional[int] = None,
                                         chat_id: Optional[int] = None,
                                         check: bool = True) -> None:

        if check:
            for i in range(len(states)):
                if i == (len(states) - 1):
                    break
                source_state = states[i]
                destination_state = states[i + 1]
                if destination_state not in self._transitions[source_state].values():
                    raise exceptions.TransitionsChronologyError(f"from '{source_state}' state it is impossible "
                                                                f"to get into '{destination_state}' state!")

        magazine = self.get_magazine(user_id, chat_id)
        await magazine.initialize(str(self.initial_state))

        for state in states:
            magazine.set(str(state))
        await magazine.commit()

        logger.debug(f"Chronology of transitions set for ({user_id=}, {chat_id=})")

    def get_magazine(self, user_id: Optional[int] = None, chat_id: Optional[int] = None) -> Magazine:

        return Magazine(storage=self._storage, user_id=user_id, chat_id=chat_id)

    @property
    def _signal_handlers(self) -> list:

        signal_handlers = []
        for handlers in [i.keys() for i in self._transitions.values()]:
            signal_handlers.extend([handler for handler in handlers if handler not in signal_handlers])

        return signal_handlers

    async def _set_state(self, state: AbstractState,
                         user_id: Optional[int] = None,
                         chat_id: Optional[int] = None) -> None:

        fsm_context = self._dispatcher.current_state(chat=chat_id, user=user_id)
        await fsm_context.set_state(state.raw_value)

        logger.debug(f"State '{state}' is set for '{user_id=}' in '{chat_id=}'")
