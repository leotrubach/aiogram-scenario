from __future__ import annotations
from typing import Optional, Dict, TYPE_CHECKING
import inspect

if TYPE_CHECKING:
    from aiogram_scenario.registrars.handlers import HandlersRegistrar


class BaseState:

    def __init__(self, *, name: Optional[str] = None):

        self.name = name or type(self).__name__
        self.enter_spec = inspect.getfullargspec(self.process_enter)
        self.exit_spec = inspect.getfullargspec(self.process_exit)

    def __str__(self):

        return self.name

    def __repr__(self):

        type_ = type(self)
        return f"<{type_.__module__}.{type_.__name__} (name={self.name!r})>"

    async def process_enter(self, *args, **kwargs) -> None:

        pass

    async def process_exit(self, *args, **kwargs) -> None:

        pass

    def register_handlers(self, registrar: HandlersRegistrar, data: Dict) -> None:

        pass
