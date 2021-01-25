from typing import Dict, Callable, Set

from aiogram_scenario.fsm.state import BaseState
from aiogram_scenario import exceptions


class TransitionsKeeper:

    def __init__(self):

        self._transitions: Dict[BaseState, Dict[Callable, BaseState]] = {}

    def __getitem__(self, item):

        return self._transitions[item]

    def __setitem__(self, key, value):

        self._transitions[key] = value

    def __iter__(self):

        return iter(self._transitions)

    def get_states(self) -> Set[BaseState]:

        states_ = set()
        for source_state in self._transitions:
            states_.add(source_state)
            for destination_state in self._transitions[source_state].values():
                states_.add(destination_state)

        return states_

    def add(self, source_state: BaseState, trigger: Callable, destination_state: BaseState) -> None:

        if source_state == destination_state:
            raise exceptions.TransitionAddingError(
                f"source state '{source_state}' is the same as destination state!"
            )

        if source_state not in self._transitions:
            self._transitions[source_state] = {trigger: destination_state}
        elif self._transitions[source_state].get(trigger) is not None:
            raise exceptions.TransitionAddingError(
                f"transition for trigger func '{trigger.__qualname__}' is "
                f"already defined in '{source_state}' state!"
            )
        else:
            self._transitions[source_state][trigger] = destination_state

    def remove(self, source_state: BaseState, trigger: Callable, destination_state: BaseState) -> None:

        if source_state == destination_state:
            raise exceptions.TransitionRemovingError(
                f"source state '{source_state}' is the same as destination state!"
            )

        try:
            if len(self._transitions[source_state]) > 1:
                del self._transitions[source_state][trigger]
            else:
                del self._transitions[source_state]
        except KeyError:
            raise exceptions.TransitionRemovingError(
                f"Transition ({source_state=}, trigger_func={trigger.__qualname__}, "
                f"{destination_state=}) not found for removing!"
            )
