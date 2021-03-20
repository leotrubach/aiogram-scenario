from typing import Dict, Optional

from .state import BaseState
from aiogram_scenario import errors


class StatesMapping:

    def __init__(self):

        self._values_states: Dict[Optional[str], BaseState] = {}
        self._states_values: Dict[BaseState, Optional[str]] = {}

    def add(self, value: Optional[str], state: BaseState):

        self._values_states[value] = state
        self._states_values[state] = value

    def remove_by_value(self, value: Optional[str]) -> None:

        state = self._values_states.pop(value)
        del self._states_values[state]

    def remove_by_state(self, state: BaseState) -> None:

        value = self._states_values.pop(state)
        del self._values_states[value]

    def get_value(self, state: BaseState) -> Optional[str]:

        try:
            return self._states_values[state]
        except KeyError:
            raise errors.StateNotFoundError(state)

    def get_state(self, value: Optional[str]) -> BaseState:

        try:
            return self._values_states[value]
        except KeyError:
            raise errors.StateValueNotFoundError(value)

    def check_value(self, value: Optional[str]) -> bool:

        return value in self._values_states

    def check_state(self, state: BaseState) -> bool:

        return state in self._states_values
