from typing import Optional, Union
import weakref

from aiogram_scenario.handlers_registrars import HandlersRegistrar
from aiogram_scenario import exceptions


class BaseState:

    __slots__ = ("name", "value", "_fsm", "_is_initial")

    def __init__(self, *, name: Optional[str] = None):

        self.name = name or self.__class__.__name__
        self.value: Union[None, str] = self.name
        self._fsm = None
        self._is_initial = None

    def __str__(self):

        return self.name

    __repr__ = __str__

    def __eq__(self, other):

        if isinstance(other, BaseState):
            return self.value == other.value

        return False

    def __hash__(self):

        return hash(tuple(vars(self).values()))

    @property
    def is_initial(self) -> bool:

        if self._fsm is None:
            raise exceptions.StateNotAddedToFSMError("it is impossible to get 'is_initial' "
                                                     "status from an unused state!")

        return self._is_initial

    @is_initial.setter
    def is_initial(self, value) -> None:

        if self._fsm is None:
            raise exceptions.StateNotAddedToFSMError("it is impossible to set 'is_initial' "
                                                     "status of an unused state!")

        self._is_initial = value

    @property
    def fsm(self):

        return self._fsm() if self._fsm is not None else None

    @fsm.setter
    def fsm(self, value):

        if value is None:
            self._fsm = value
            self._is_initial = None
        else:
            self._fsm = weakref.ref(value)

    async def process_enter(self, *args, **kwargs) -> None:

        pass

    async def process_exit(self, *args, **kwargs) -> None:

        pass

    def register_handlers(self, registrar: HandlersRegistrar, data: dict) -> None:

        pass
