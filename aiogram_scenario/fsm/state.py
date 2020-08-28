from abc import ABC, abstractmethod
from typing import Optional


class AbstractState(ABC):

    def __init__(self, is_initial: bool = False):

        self.name = self.__class__.__name__
        self._is_initial = is_initial

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

    @abstractmethod
    def register_handlers(self, *args, **reg_kwargs) -> None:

        pass

    @property
    def is_initial(self) -> bool:

        return self._is_initial

    @property
    def raw_value(self) -> Optional[str]:

        if self._is_initial:
            return None
        else:
            return str(self)
