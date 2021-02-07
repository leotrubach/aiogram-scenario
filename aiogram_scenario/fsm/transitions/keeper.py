from typing import Optional, Set

from aiogram_scenario.fsm.state import BaseState
from aiogram_scenario.fsm.types import TransitionsType
from aiogram_scenario import exceptions


class TransitionsKeeper:

    def __init__(self):

        self._transitions: TransitionsType = {}

    def __getitem__(self, item):

        return self._transitions[item]

    def get_states(self) -> Set[BaseState]:

        states = set()
        for source_state in self._transitions:
            states.add(source_state)
            for handler in self._transitions[source_state]:
                for _, destination_state in self._transitions[source_state][handler].items():
                    states.add(destination_state)

        return states

    def add(self, source_state: BaseState, destination_state: BaseState,
            handler: str, direction: Optional[str] = None) -> None:

        if source_state == destination_state:
            raise ValueError(f"source state '{source_state}' is the same as destination state!")

        if source_state not in self._transitions:
            self._transitions[source_state] = {
                handler: {
                    direction: destination_state
                }
            }
        elif handler not in self._transitions[source_state]:
            self._transitions[source_state][handler] = {
                direction: destination_state
            }
        elif direction not in self._transitions[source_state][handler]:
            self._transitions[source_state][handler][direction] = destination_state
        else:
            raise exceptions.TransitionAddingError(
                f"transition is already defined ({source_state=}, {handler=}, {direction=})!"
            )

    def remove(self, source_state: BaseState, destination_state: BaseState,
               handler: str, direction: Optional[str] = None) -> None:

        if source_state == destination_state:
            raise ValueError(f"source state '{source_state}' is the same as destination state!")

        try:
            del self._transitions[source_state][handler][direction]
        except KeyError:
            raise exceptions.TransitionRemovingError(
                f"transition not found for removing ({source_state=}, {handler=}, {direction=}, {destination_state=})!"
            )

        if not self._transitions[source_state][handler]:
            del self._transitions[source_state][handler]
        if not self._transitions[source_state]:
            del self._transitions[source_state]
