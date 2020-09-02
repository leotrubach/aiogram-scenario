from typing import Dict, Callable, Set
import logging

from aiogram_scenario.fsm.state import AbstractState
from aiogram_scenario import exceptions


logger = logging.getLogger(__name__)


def _check_equivalent_states(source_state: AbstractState, destination_state: AbstractState) -> None:

    if source_state == destination_state:
        raise exceptions.fsm.TransitionAddingError(
            f"source state '{source_state}' is the same as destination state!"
        )


class TransitionsKeeper:

    def __init__(self):

        self._transitions: Dict[AbstractState, Dict[Callable, AbstractState]] = {}
        self._states: Set[AbstractState] = set()
        self._source_states: Set[AbstractState] = set()

    def __getitem__(self, item):

        return self._transitions[item]

    def __setitem__(self, key, value):

        self._transitions[key] = value

    @property
    def serialized_transitions(self) -> Dict[str, Dict[str, str]]:

        return {
            str(source_state): {
                trigger_func.__name__: str(destination_state)
                for trigger_func, destination_state in self._transitions[source_state].items()
            }
            for source_state in self._transitions.keys()
        }

    @property
    def source_states(self) -> Set[AbstractState]:

        return self._source_states

    @property
    def states(self) -> Set[AbstractState]:

        return self._states

    def add_transition(self, source_state: AbstractState,
                       trigger_func: Callable,
                       destination_state: AbstractState) -> None:

        _check_equivalent_states(source_state, destination_state)

        if source_state not in self._source_states:
            self._transitions[source_state] = {trigger_func: destination_state}
        elif self._transitions[source_state].get(trigger_func) is not None:
            raise exceptions.fsm.TransitionAddingError(
                f"transition for trigger func '{trigger_func.__qualname__}' is "
                f"already defined in '{source_state}' state!"
            )
        else:
            self._transitions[source_state][trigger_func] = destination_state

        self._source_states.add(source_state)
        for state in (source_state, destination_state):
            self._states.add(state)

        logger.debug(f"Added transition from '{source_state}' "
                     f"('{trigger_func.__qualname__}') to '{destination_state}'")

    def remove_transition(self, source_state: AbstractState,
                          trigger_func: Callable,
                          destination_state: AbstractState) -> None:

        _check_equivalent_states(source_state, destination_state)

        del self._transitions[source_state][trigger_func]
        if not self._transitions[source_state]:
            del self._transitions[source_state]
            self._source_states.remove(source_state)

        states = list(self._transitions.keys())
        for i in self._transitions.values():
            states.extend(i.values())
        states = set(states)

        for state in (source_state, destination_state):
            if state not in states:
                self._states.remove(state)
