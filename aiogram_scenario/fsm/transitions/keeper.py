from typing import Optional, Set

from aiogram_scenario.fsm.state import BaseState
from aiogram_scenario.fsm.types import TransitionsType
from aiogram_scenario import errors


class TransitionsKeeper:

    def __init__(self):

        self._transitions: TransitionsType = {}
        self._states = set()

    @property
    def states(self) -> Set[BaseState]:

        return self._states.copy()

    def add(self, *, source_state: BaseState, destination_state: BaseState,
            handler: str, direction: Optional[str] = None) -> None:

        if source_state not in self._transitions:
            self._transitions[source_state] = {
                handler: {
                    direction: destination_state
                }
            }
            self._states.add(source_state)
        elif handler not in self._transitions[source_state]:
            self._transitions[source_state][handler] = {
                direction: destination_state
            }
        elif direction not in self._transitions[source_state][handler]:
            self._transitions[source_state][handler][direction] = destination_state
        else:
            raise errors.TransitionIsExistsError(
                source_state=source_state,
                existing_destination_state=self._transitions[source_state][handler][direction],
                handler=handler,
                direction=direction
            )

        self._states.add(destination_state)

    def check(self, *, source_state: BaseState, destination_state: BaseState,
              handler: str, direction: Optional[str] = None) -> bool:

        try:
            return self._transitions[source_state][handler][direction] is destination_state
        except KeyError:
            return False

    def remove(self, *, source_state: BaseState, handler: str, direction: Optional[str] = None) -> BaseState:

        try:
            destination_state = self._transitions[source_state][handler].pop(direction)
        except KeyError:
            raise errors.TransitionRemovingError(source_state, handler, direction)

        if not self._transitions[source_state][handler]:
            del self._transitions[source_state][handler]
        if not self._transitions[source_state]:
            del self._transitions[source_state]

        existing_states = set()
        for source_state_ in self._transitions:
            existing_states.add(source_state_)
            for handler in self._transitions[source_state]:
                for destination_state_ in self._transitions[source_state][handler].values():
                    existing_states.add(destination_state_)

        for state in (source_state, destination_state):
            if state not in existing_states:
                self._states.remove(state)

        return destination_state

    def get_destination_state(self, source_state: BaseState,
                              handler: str, direction: Optional[str] = None) -> BaseState:

        try:
            return self._transitions[source_state][handler][direction]
        except KeyError:
            raise errors.TransitionNotFoundError(source_state=source_state, handler=handler,
                                                 direction=direction)
