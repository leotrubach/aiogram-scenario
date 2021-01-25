from typing import Dict
import json

from .base import AbstractTransitionsAdapter


class JSONTransitionsAdapter(AbstractTransitionsAdapter):

    def parse_transitions(self, content: str) -> Dict[str, Dict[str, str]]:

        return json.loads(content)
