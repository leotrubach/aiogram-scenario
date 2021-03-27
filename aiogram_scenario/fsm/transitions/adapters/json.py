from typing import Dict
import json

from .base import AbstractTransitionsAdapter


class JSONTransitionsAdapter(AbstractTransitionsAdapter):

    def _parse(self, content: str) -> Dict[str, Dict[str, str]]:

        raw_transitions = json.loads(content)
        transitions = {}

        for source_state in raw_transitions:
            transitions[source_state] = {}
            for handler in raw_transitions[source_state]:
                transitions[source_state][handler] = {}
                element = raw_transitions[source_state][handler]
                if isinstance(element, str):
                    transitions[source_state][handler][None] = element
                elif isinstance(element, dict):
                    for direction, destination_state in element.items():
                        transitions[source_state][handler][direction] = destination_state

        return transitions