from typing import Dict
import json

from .base import AbstractTransitionsAdapter


class JSONTransitionsAdapter(AbstractTransitionsAdapter):

    def __init__(self, *, optional_direction: str = ""):

        self._optional_direction = optional_direction

    def parse_transitions(self, content: str) -> Dict[str, Dict[str, str]]:

        raw_transitions = json.loads(content)
        transitions = {}

        for source_state in raw_transitions:
            transitions[source_state] = {}
            for handler in raw_transitions[source_state]:
                transitions[source_state][handler] = {}
                for raw_direction, destination_state in raw_transitions[source_state][handler].items():
                    direction = None if raw_direction == self._optional_direction else raw_direction
                    transitions[source_state][handler][direction] = destination_state

        return transitions
