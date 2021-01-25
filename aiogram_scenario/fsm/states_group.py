from typing import Collection, List

from .state import BaseState


class BaseStatesGroup:

    @classmethod
    def select(cls, *, exclude: Collection[BaseState] = ()) -> List[BaseState]:

        cls_values = vars(cls).values()
        states = [i for i in cls_values if isinstance(i, BaseState) and (i not in exclude)]

        return states
