from abc import ABC, abstractmethod
from typing import Optional, Dict, Union
import re

from aiogram_scenario.fsm.types import RawTransitionsType


RawBaseTransitionsType = Dict[str, Dict[str, Union[str, Dict[str, str]]]]


def _get_new_name(name: str, prefix: Optional[str], postfix: Optional[str]) -> str:

    if prefix and postfix:
        return f"{prefix}{name}{postfix}"
    elif prefix:
        return f"{prefix}{name}"
    elif postfix:
        return f"{name}{postfix}"
    else:
        return name


def _check_state_name(name: str) -> None:

    if re.fullmatch(r"[a-zA-Z_]\w*", name) is None:
        raise ValueError(f"incorrect state name '{name}'!")


def _check_handler_name(name: str) -> None:

    if re.fullmatch(r"[a-zA-Z_]\w*", name) is None:
        raise ValueError(f"incorrect handler name '{name}'!")


def _check_direction_name(name: Optional[str]) -> None:

    if (name is not None) and (re.fullmatch(r"\S+", name) is None):
        raise ValueError(f"incorrect direction name '{name}'!")


def _check_naming(transitions: RawTransitionsType) -> None:

    for source_state in transitions:
        _check_state_name(source_state)
        for handler in transitions[source_state]:
            _check_handler_name(handler)
            element = transitions[source_state][handler]
            if isinstance(element, str):
                _check_state_name(element)
            elif isinstance(element, dict):
                for direction, destination_state in element.items():
                    _check_direction_name(direction)
                    _check_state_name(destination_state)


def _get_augmented_transitions(transitions: RawTransitionsType, handlers_prefix: Optional[str],
                               handlers_postfix: Optional[str], states_prefix: Optional[str],
                               states_postfix: Optional[str]) -> RawTransitionsType:

    augmented_transitions = {}
    for source_state in transitions:
        new_source_state = _get_new_name(source_state, states_prefix, states_postfix)
        augmented_transitions[new_source_state] = {}

        for handler in transitions[source_state]:
            new_handler = _get_new_name(handler, handlers_prefix, handlers_postfix)
            augmented_transitions[new_source_state][new_handler] = {}

            for direction, destination_state in transitions[source_state][handler].items():
                new_destination_state = _get_new_name(destination_state, states_prefix, states_postfix)
                augmented_transitions[new_source_state][new_handler][direction] = new_destination_state

    return augmented_transitions


def _get_transitions_with_optional_directions(transitions: RawBaseTransitionsType) -> RawTransitionsType:

    transitions_ = {}
    for source_state in transitions:
        transitions_[source_state] = {}
        for handler in transitions[source_state]:
            transitions_[source_state][handler] = {}
            element = transitions[source_state][handler]
            if isinstance(element, str):
                transitions_[source_state][handler][None] = element
            elif isinstance(element, dict):
                for direction, destination_state in element.items():
                    transitions_[source_state][handler][direction] = destination_state

    return transitions_


class AbstractTransitionsAdapter(ABC):

    def load(self, filename: str, encoding: str = "UTF-8", *,
             handlers_prefix: Optional[str] = None,
             handlers_postfix: Optional[str] = None,
             states_prefix: Optional[str] = None,
             states_postfix: Optional[str] = None) -> RawTransitionsType:

        content = self._fetch(filename, encoding)
        transitions = self._parse(content)

        _check_naming(transitions)
        transitions = _get_transitions_with_optional_directions(transitions)

        if any((handlers_prefix, handlers_postfix, states_prefix, states_postfix)):
            transitions = _get_augmented_transitions(transitions, handlers_prefix, handlers_postfix,
                                                     states_prefix, states_postfix)

        return transitions

    # noinspection PyMethodMayBeStatic
    def _fetch(self, filename: str, encoding: str) -> str:

        with open(filename, encoding=encoding) as file_wrapper:
            content = file_wrapper.read()

        return content

    @abstractmethod
    def _parse(self, content: str) -> RawBaseTransitionsType:

        pass
