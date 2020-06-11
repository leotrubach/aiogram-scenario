from typing import Callable, List, Optional
from dataclasses import dataclass

from .state import AbstractState


@dataclass()
class StateWay:
    """ Dataclass, which includes the target target_state and the possible ways that lead to it. """

    target_state: AbstractState
    pointing_handlers: List[Callable]


class StatesMap:
    """ The target_state map allows you to flexibly configure transitions between states.
        It requires the mandatory transfer of the initial target_state, for its correct registration.
    """

    def __init__(self, start_state: AbstractState):

        self._states_ways: List[StateWay] = []
        self._start_state = start_state
        self._start_state.name = None

    def add_way(self, target_state: AbstractState, pointing_handlers: List[Callable]) -> None:
        """ Adds a new target target_state and possible ways to it. """

        if not self._check_state_existence(target_state):
            state_way = StateWay(target_state, pointing_handlers)
            self._states_ways.append(state_way)
        else:
            raise RuntimeError("StateWay with this target_state has already been added before!")

    def get_target_state(self, pointing_handler: Callable) -> Optional[AbstractState]:
        """ Gets the target target_state using a pointing handler. """

        for state_way in self._states_ways:
            if pointing_handler in state_way.pointing_handlers:
                return state_way.target_state

    @property
    def states(self) -> List[AbstractState]:
        """ Allows you to get a list of all map states. """

        states = [self._start_state]
        states.extend([state_way.target_state for state_way in self._states_ways])
        return states

    def _check_state_existence(self, state: AbstractState) -> bool:
        """ Checks target_state for existence. """

        for state_way in self._states_ways:
            if state == state_way.target_state:
                return True
        return False
