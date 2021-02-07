from typing import Dict, Optional, Union

from .state import BaseState


class StatesMapping:

    def __init__(self):

        self._values_states: Dict[Optional[str], BaseState] = {}
        self._states_values: Dict[BaseState, Optional[str]] = {}

    def __setitem__(self, key: Optional[str], value: BaseState):

        self._values_states[key] = value
        self._states_values[value] = key

    def __delitem__(self, key: Union[Optional[str], BaseState]):

        if (key is None) or isinstance(key, str):
            state = self._values_states.pop(key)
            del self._states_values[state]
        elif isinstance(key, BaseState):
            value = self._states_values.pop(key)
            del self._values_states[value]
        else:
            raise TypeError(f"incorrect type key '{type(key).__name__}'!")

    def get_value(self, state: BaseState) -> Optional[str]:

        return self._states_values[state]

    def get_state(self, value: Optional[str]) -> BaseState:

        return self._values_states[value]

    def check_existence(self, state: Union[Optional[str], BaseState]) -> bool:

        if (state is None) or isinstance(state, str):
            return state in self._values_states
        elif isinstance(state, BaseState):
            return state in self._states_values
        else:
            raise TypeError(f"incorrect type state '{type(state).__name__}'!")
