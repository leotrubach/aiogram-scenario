from abc import ABC, abstractmethod


class AbstractState(ABC):
    """ An abstract target_state class, used to define eigenstates.

        To describe your own target_state:
            - Inherit from this class.
            - Define asynchronous handlers.
            - Register the new handlers in the register_handlers abstract method.
            - Set the transition logic in the process_transition method.
    """

    def __init__(self):

        self.name = self.__class__.__name__

    def __str__(self):

        return self.name

    @abstractmethod
    async def process_transition(self, *args, **kwargs) -> None:
        """ Performs target_state transition logic.
            It has all the same arguments as the handler.
        """

        pass

    @abstractmethod
    def register_handlers(self, *args, **kwargs) -> None:
        """ Registers target_state handlers. """

        pass
