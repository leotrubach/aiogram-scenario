from typing import Optional

from .state import AbstractState


class StatesGroup:

    @classmethod
    def get_states(cls, exclude: Optional[list] = None):

        states = [i for i in cls.__dict__.values() if isinstance(i, AbstractState)]

        if exclude:
            states = [i for i in states if i not in exclude]

        return states
