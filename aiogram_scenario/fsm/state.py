from abc import ABC, abstractmethod
from typing import Optional


class AbstractState(ABC):

    def __init__(self):

        self.name = self.__class__.__name__
        self._is_assigned = False
        self.is_initial = False
        self.handlers = []

    def __str__(self):

        return self.name

    __repr__ = __str__

    def __eq__(self, other):

        return self.name == other

    def __hash__(self):

        return hash(self.name)

    async def process_enter(self, *args, **kwargs) -> None:

        pass

    async def process_exit(self, *args, **kwargs) -> None:

        pass

    @property
    def raw_value(self):

        if self.is_initial:
            return None
        else:
            return str(self)

    @property
    def is_assigned(self) -> bool:

        return self._is_assigned

    @is_assigned.setter
    def is_assigned(self, value: bool) -> None:

        if value is False:
            self.is_initial = False
        self._is_assigned = value

    @abstractmethod
    def register_handlers(self, *args, **reg_kwargs) -> None:

        pass
