from typing import Dict, Optional
from collections import namedtuple

try:
    import lxml.etree  # noqa
except ImportError:
    lxml = None

from .base import AbstractTransitionsStorage


StateObject = namedtuple("StateObject", ("id", "name"))
TransitionObject = namedtuple("TransitionObject", ("id", "trigger", "connections"))


def _parse_state_element(element, element_id) -> Optional[StateObject]:

    for element_attr in element.getchildren():
        if element_attr.get("name") == "text":
            for composite in element_attr.getchildren():
                if composite.get("type") == "text":
                    for composite_attr in composite.getchildren():
                        if composite_attr.get("name") == "string":
                            state_name = composite_attr.getchildren()[0].text.strip("#")
                            state_object = StateObject(id=element_id, name=state_name)

                            return state_object


def _parse_transition_element(element, element_id) -> Optional[TransitionObject]:

    transition_trigger = None
    transition_connections = None
    for element_attr in element.getchildren():
        if element_attr.get("name") == "trigger":
            transition_trigger = element_attr.getchildren()[0].text.strip("#")
        if element_attr.tag.endswith("connections"):
            transition_connections = tuple(i.get("to") for i in element_attr.getchildren())
            if len(transition_connections) != 2:
                break

        if all(i is not None for i in (transition_trigger, transition_connections)):
            transition_object = TransitionObject(id=element_id, trigger=transition_trigger,
                                                 connections=transition_connections)
            return transition_object


def _get_transitions(states_objects, transitions_objects):

    transitions = {}
    for transition_object in transitions_objects:
        source_state = None
        destination_state = None
        for state_object in states_objects:
            if state_object.id == transition_object.connections[0]:
                source_state = state_object.name
            elif state_object.id == transition_object.connections[1]:
                destination_state = state_object.name
            if all(i is not None for i in (source_state, destination_state)):
                break

        if source_state not in transitions.keys():
            transitions[source_state] = {transition_object.trigger: destination_state}
        else:
            transitions[source_state][transition_object.trigger] = destination_state

    return transitions


class DiaTransitionsStorage(AbstractTransitionsStorage):

    def read(self) -> Dict[str, Dict[str, str]]:

        if lxml is None:
            raise RuntimeError("parsing structure of the «.dia» file requires the «lxml» library to be installed!\n"
                               "More details: https://lxml.de/installation.html#installation")

        tree = lxml.etree.parse(self._filename)
        root = tree.getroot()
        _, layer = root.getchildren()

        states_objects = []
        transitions_objects = []
        for element in layer:

            if not element.tag.endswith("object"):
                continue

            element_type = element.get("type")
            element_id = element.get("id")

            if element_type == "UML - State":
                state_object = _parse_state_element(element, element_id)
                if state_object is not None:
                    states_objects.append(state_object)
            elif element_type == "UML - Transition":
                transition_object = _parse_transition_element(element, element_id)
                if transition_object is not None:
                    transitions_objects.append(transition_object)

        transitions = _get_transitions(states_objects, transitions_objects)

        return transitions

    def write(self, transitions: Dict[str, Dict[str, str]]) -> None:

        raise RuntimeError("the ability to generate Dia schema from source data is not yet available!")
