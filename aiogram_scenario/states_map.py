from typing import Callable, List, Optional, Dict
from dataclasses import dataclass
import logging

from .state import AbstractState


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
        self._routes: List[StateRouting] = []

    def add_routes(self, routes: Dict[AbstractState, List[Callable]]):

        for target_state, pointing_handlers in routes.items():
            state_routing = StateRouting(target_state, pointing_handlers)
            self._routes.append(state_routing)
            logger.debug(f"Added routes: {target_state}' - "
                         f'{" ,".join([i.__qualname__ for i in pointing_handlers])}')

    @property
    def routes(self):

        if not self._routes:
            raise RuntimeError("No routes set!")

        return self._routes

    def get_target_state(self, pointing_handler: Callable) -> Optional[AbstractState]:
        """ Gets the target target_state using a pointing handler. """

        for routing in self.routes:
            if pointing_handler in routing.pointing_handlers:
                return routing.target_state
