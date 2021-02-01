from typing import Union

from .state import BaseState


class StatesMapping:

    def __init__(self):

        self.values_states = {}
        self.states_values = {}

    def __setitem__(self, key: Union[None, str], value: BaseState):

        self.values_states[key] = value
        self.states_values[value] = key

    def __delitem__(self, key: Union[None, str]):

        state = self.values_states.pop(key)
        del self.states_values[state]
