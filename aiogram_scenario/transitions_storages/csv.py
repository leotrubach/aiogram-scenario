from typing import Dict

import csv

from .base import AbstractTransitionsStorage


class CSVTransitionsStorage(AbstractTransitionsStorage):

    def read(self) -> Dict[str, Dict[str, str]]:

        with open(self._filename, newline="") as csv_fp:
            reader = csv.reader(csv_fp)
            rows = list(reader)

        source_states = rows[0][1:]
        transitions = {source_state: {} for source_state in source_states}
        for row in rows[1:]:
            signal_handler = row[0]
            for index, destination_state in enumerate(row[1:]):
                if destination_state:
                    source_state = source_states[index]
                    transitions[source_state][signal_handler] = destination_state

        return transitions

    def write(self, transitions: Dict[str, Dict[str, str]]) -> None:

        signal_handlers = []
        for handlers in (i.keys() for i in transitions.values()):
            for handler in handlers:
                if handler not in signal_handlers:
                    signal_handlers.append(handler)

        rows = [["", *transitions.keys()]]
        for signal_handler in signal_handlers:
            destination_states = []
            for source_state in transitions.keys():
                destination_state = transitions[source_state].get(signal_handler)
                if destination_state is None:
                    destination_states.append("")
                else:
                    destination_states.append(destination_state)
            rows.append([signal_handler, *destination_states])

        with open(self._filename, "w", newline="") as csv_fp:
            writer = csv.writer(csv_fp)
            writer.writerows(rows)
