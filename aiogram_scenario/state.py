from abc import ABC, abstractmethod


class AbstractState(ABC):

    def __init__(self):

        self.name = self.__class__.__name__

    def __str__(self):

        return self.name

    @abstractmethod
    async def process_transition(self, *args, **kwargs) -> None:

        pass

    @abstractmethod
    def register_handlers(self, *args, **kwargs) -> None:

        pass
