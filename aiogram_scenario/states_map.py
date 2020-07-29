from typing import Callable, List, Optional, Dict, Union, Iterable
from dataclasses import dataclass
import logging

from .state import AbstractState
from . import exceptions


logger = logging.getLogger(__name__)


class PointingHandler:

    def __init__(self, callback: Callable, **conditions):

        self.callback = callback
        self.conditions = conditions


@dataclass()
class StatesRouting:
    """ Dataclass, which includes the target target_state and the possible ways that lead to it. """

    target_state: AbstractState
    pointing_handlers: List[PointingHandler]


class StatesMap:
    """ The target_state map allows you to flexibly configure transitions between states.
        It requires the mandatory transfer of the initial target_state, for its correct registration.
    """

    def __init__(self, start_state: AbstractState):

        self.start_state = start_state
        self._routings: List[StatesRouting] = []

    def add_routings(self, routings: Dict[AbstractState, Iterable[Union[PointingHandler, Callable]]]):

        existing_states = [i.target_state for i in self._routings]
        for target_state in routings.keys():
            if target_state in existing_states:
                raise RuntimeError(f"this state already exists: '{target_state.name}'")

        for target_state, pointing_handlers in routings.items():
            pointing_handlers = [i if isinstance(i, PointingHandler) else PointingHandler(i)
                                 for i in pointing_handlers]
            routing = StatesRouting(target_state, pointing_handlers)
            self._routings.append(routing)
            logger.debug(f"Added routings: '{target_state}' - "
                         f'{", ".join([i.callback.__qualname__ for i in pointing_handlers])}')

    @property
    def routings(self) -> List[StatesRouting]:

        if not self._routings:
            raise RuntimeError("No routings set!")

        return self._routings

    def get_state_by_handler(self, pointing_handler: Callable,
                             conditions: Optional[dict] = None) -> AbstractState:
        """ Gets the target target_state using a pointing handler. """

        if conditions is None:
            conditions = {}

        for routing in self.routings:
            for routing_handler in routing.pointing_handlers:
                if (pointing_handler == routing_handler.callback) and (conditions == routing_handler.conditions):
                    return routing.target_state
        else:
            raise exceptions.TargetStateNotFoundError(f"target state not found for handler "
                                                      f"'{pointing_handler.__qualname__}' ")

    def get_state_by_name(self, state_name: str) -> AbstractState:

        for routing in self._routings:
            state = routing.target_state
            if state.name == state_name:
                return state
