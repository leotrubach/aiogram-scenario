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
            trigger_func = row[0]
            for index, destination_state in enumerate(row[1:]):
                if destination_state:
                    source_state = source_states[index]
                    transitions[source_state][trigger_func] = destination_state

        return transitions

    def write(self, transitions: Dict[str, Dict[str, str]]) -> None:

        triggers_funcs = []
        for funcs in (i.keys() for i in transitions.values()):
            for func in funcs:
                if func not in triggers_funcs:
                    triggers_funcs.append(func)

        rows = [["", *transitions.keys()]]
        for trigger_func in triggers_funcs:
            destination_states = []
            for source_state in transitions.keys():
                destination_state = transitions[source_state].get(trigger_func)
                if destination_state is None:
                    destination_states.append("")
                else:
                    destination_states.append(destination_state)
            rows.append([trigger_func, *destination_states])

        with open(self._filename, "w", newline="") as csv_fp:
            writer = csv.writer(csv_fp)
            writer.writerows(rows)
