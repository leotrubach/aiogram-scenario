from typing import Callable, List, Optional, Dict
from dataclasses import dataclass
import logging

from .state import AbstractState
from . import exceptions


logger = logging.getLogger(__name__)


@dataclass()
class StateRouting:
    """ Dataclass, which includes the target target_state and the possible ways that lead to it. """

    target_state: AbstractState
    pointing_handlers: List[Callable]


class StatesMap:
    """ The target_state map allows you to flexibly configure transitions between states.
        It requires the mandatory transfer of the initial target_state, for its correct registration.
    """

    def __init__(self, start_state: AbstractState):

        self.start_state = start_state
        self._routings: List[StateRouting] = []

    def add_routings(self, routings: Dict[AbstractState, List[Callable]]):

        states_names = [i.name for i in routings]
        for name in states_names:
            if states_names.count(name) > 1:
                raise RuntimeError(f"not all states have a unique name: '{name}'")

        for target_state, pointing_handlers in routings.items():
            state_routing = StateRouting(target_state, pointing_handlers)
            self._routings.append(state_routing)
            logger.debug(f"Added routings: '{target_state}' - "
                         f'{", ".join([i.__qualname__ for i in pointing_handlers])}')

    @property
    def routings(self):

        if not self._routings:
            raise RuntimeError("No routings set!")

        return self._routings

    def get_state_by_handler(self, pointing_handler: Callable) -> Optional[AbstractState]:
        """ Gets the target target_state using a pointing handler. """

        for routing in self.routings:
            if pointing_handler in routing.pointing_handlers:
                return routing.target_state
        else:
            raise exceptions.TargetStateNotFoundError(f"target state not found for handler "
                                                      f"'{pointing_handler.__qualname__}' ")

    def get_state_by_name(self, state_name: str) -> AbstractState:

        for routing in self._routings:
            state = routing.target_state
            if state.name == state_name:
                return state
