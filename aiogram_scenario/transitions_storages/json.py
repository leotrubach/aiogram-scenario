from .base import AbstractTransitionsStorage
from typing import Dict

import json


class JSONTransitionsStorage(AbstractTransitionsStorage):

    def read(self) -> Dict[str, Dict[str, str]]:

        with open(self._filename) as json_file:
            transitions = json.load(json_file)

        return transitions

    def write(self, transitions: Dict[str, Dict[str, str]]) -> None:

        with open(self._filename, "w") as json_file:
            json.dump(transitions, json_file, indent=4)
