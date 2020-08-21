from typing import Optional, Collection

from .state import AbstractState


class StatesGroup:

    @classmethod
    def get_states(cls, exclude: Optional[Collection[AbstractState]] = None):

        cls_values = cls.__dict__.values()

        if exclude is None:
            states = [i for i in cls_values if isinstance(i, AbstractState)]
        else:
            states = [i for i in cls_values if isinstance(i, AbstractState) and (i not in exclude)]

        return states
