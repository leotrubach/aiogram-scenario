from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram_scenario.registrars.handlers import HandlersRegistrar


class BaseState:

    __slots__ = ("name",)

    def __init__(self, *, name: Optional[str] = None):

        self.name = name or self.__class__.__name__

    def __str__(self):

        return self.name

    __repr__ = __str__

    def __eq__(self, other):

        if isinstance(other, BaseState):
            return self.name == other.name

        return False

    def __hash__(self):

        return hash(tuple(vars(self).values()))

    async def process_enter(self, *args, **kwargs) -> None:

        pass

    async def process_exit(self, *args, **kwargs) -> None:

        pass

    def register_handlers(self, registrar: HandlersRegistrar, data: dict) -> None:

        pass
