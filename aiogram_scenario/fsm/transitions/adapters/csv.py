from typing import Dict
import csv

from .base import AbstractTransitionsAdapter


class CSVTransitionsAdapter(AbstractTransitionsAdapter):

    def __init__(self, filename: str, delimiter: str = ","):

        super().__init__(filename)
        self._delimiter = delimiter

    def fetch_content(self, filename: str, encoding: str) -> str:

        with open(filename, encoding=encoding, newline="") as file_wrapper:
            content = file_wrapper.read()

        return content

    def parse_transitions(self, content: str) -> Dict[str, Dict[str, str]]:

        reader = csv.reader(content.splitlines(), delimiter=self._delimiter)
        rows = list(reader)

        source_states = rows[0][1:]
        transitions = {source_state: {} for source_state in source_states}
        for row in rows[1:]:
            trigger_func = row[0]
            for index, destination_state in enumerate(row[1:]):
                if destination_state:
                    source_state = source_states[index]
                    transitions[source_state][trigger_func] = destination_state

        return transitions
