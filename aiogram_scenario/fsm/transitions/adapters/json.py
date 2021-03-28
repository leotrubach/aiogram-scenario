import json

from .base import AbstractTransitionsAdapter, RawBaseTransitionsType


class JSONTransitionsAdapter(AbstractTransitionsAdapter):

    def _parse(self, content: str) -> RawBaseTransitionsType:

        return json.loads(content)
