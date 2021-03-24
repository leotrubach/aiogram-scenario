from typing import Collection, FrozenSet

from .state import BaseState


class StatesGroup:

    def __init__(self, *states: BaseState):

        self._states = frozenset(states)

    def __len__(self):

        return len(self._states)

    def __iter__(self):

        return iter(self._states)

    def __contains__(self, state: BaseState):

        return state in self._states

    def select(self, *, exclude: Collection[BaseState] = ()) -> FrozenSet[BaseState]:

        if not exclude:
            return self._states
        else:
            return frozenset({i for i in self._states if i not in exclude})
