from abc import ABC, abstractmethod
from typing import Dict, Optional
import string


_IDENTIFIER_VALID_CHARACTERS = string.ascii_letters + string.digits + "_"


def _get_new_name(name: str, prefix: Optional[str] = None,
                  postfix: Optional[str] = None) -> str:

    if prefix and postfix:
        return f"{prefix}{name}{postfix}"
    elif prefix:
        return f"{prefix}{name}"
    elif postfix:
        return f"{name}{postfix}"
    else:
        return name


def _check_correct_name(name: str) -> bool:

    return (all(not name.startswith(i) for i in string.digits)
            and
            all(i in _IDENTIFIER_VALID_CHARACTERS for i in name))


class AbstractTransitionsAdapter(ABC):

    def __init__(self, filename: str):

        self.filename = filename

    def fetch_content(self) -> str:

        with open(self.filename) as file_wrapper:
            content = file_wrapper.read()

        return content

    @abstractmethod
    def parse_transitions(self, content: str) -> Dict[str, Dict[str, str]]:

        pass

    def get_transitions(self, *, triggers_prefix: Optional[str] = None,
                        triggers_postfix: Optional[str] = None,
                        states_prefix: Optional[str] = None,
                        states_postfix: Optional[str] = None) -> Dict[str, Dict[str, str]]:

        content = self.fetch_content()
        transitions = self.parse_transitions(content)

        states = {transitions}
        for source_state in transitions:
            states.add(source_state)
            states.update(transitions[source_state].values())
        for state in states:
            if not _check_correct_name(state):
                raise ValueError(f"state '{state}' has an invalid name!")

        for source_state in transitions:
            for trigger in transitions[source_state]:
                if not _check_correct_name(trigger):
                    raise ValueError(f"trigger '{trigger}' has an invalid name!")

        if any((triggers_prefix, triggers_postfix, states_prefix, states_postfix)):
            new_transitions = {}
            for source_state in transitions:
                source_state_key = _get_new_name(source_state, states_prefix, states_postfix)
                new_transitions[source_state_key] = {}

                for trigger in transitions[source_state]:
                    trigger_key = _get_new_name(trigger, triggers_prefix, triggers_postfix)
                    destination_state_key = _get_new_name(transitions[source_state][trigger],
                                                          states_prefix, states_postfix)
                    new_transitions[source_state_key][trigger_key] = destination_state_key

            return new_transitions

        return transitions
