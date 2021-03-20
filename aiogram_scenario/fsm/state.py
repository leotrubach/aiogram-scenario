from __future__ import annotations
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram_scenario.registrars.handlers import HandlersRegistrar


class BaseState:

    __slots__ = ("name",)

    def __init__(self, *, name: Optional[str] = None):

        self.name = name or type(self).__name__

    def __str__(self):

        return self.name

    def __repr__(self):

        type_ = type(self)
        return f"<{type_.__module__}.{type_.__name__} (name={self.name!r})>"

    def __eq__(self, other):

        if isinstance(other, BaseState):
            return self.name == other.name

        return False

    def __hash__(self):

        return hash(self.__hash_key)

    async def process_enter(self, *args, **kwargs) -> None:

        pass

    async def process_exit(self, *args, **kwargs) -> None:

        pass

    def register_handlers(self, registrar: HandlersRegistrar, data: Dict) -> None:

        pass

    @property
    def __hash_key(self) -> tuple:

        return self.name,
