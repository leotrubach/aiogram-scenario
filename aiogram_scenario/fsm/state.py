from abc import ABC, abstractmethod


class AbstractState(ABC):

    def __init__(self):

        self.name = self.__class__.__name__
        self.raw_value = self.name

    def __str__(self):

        return self.name

    __repr__ = __str__

    def __eq__(self, other):

        return self.name == other

    async def process_enter(self, *args, **kwargs) -> None:

        pass

    async def process_exit(self, *args, **kwargs) -> None:

        pass

    @abstractmethod
    def register_handlers(self, *args, **reg_kwargs) -> None:

        pass
