from typing import Optional, Collection, List

from .state import AbstractState


class BaseStatesGroup:

    @classmethod
    def select(cls, exclude: Optional[Collection[AbstractState]] = None) -> List[AbstractState]:

        cls_values = cls.__dict__.values()

        if exclude is None:
            states = [i for i in cls_values if isinstance(i, AbstractState)]
        else:
            states = [i for i in cls_values if isinstance(i, AbstractState) and (i not in exclude)]

        return states
