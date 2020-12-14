from aiogram_scenario.registrars import MainRegistrar

from ..fsm.states_group import StatesGroup
from . import common


def register_handlers(registrar: MainRegistrar, **reg_kwargs) -> None:
    registrar.register_fsm_handlers(StatesGroup.select(), **reg_kwargs)
    ...  # register other handlers here, for example, a common handler for several states, or an error handler
