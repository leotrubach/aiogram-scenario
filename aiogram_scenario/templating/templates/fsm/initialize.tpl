from aiogram_scenario import FiniteStateMachine
from aiogram_scenario.transitions_storages.base import AbstractTransitionsStorage

from .states_group import StatesGroup
{states_modules_imports}


def initialize(fsm: FiniteStateMachine, storage: AbstractTransitionsStorage) -> None:
    fsm.set_initial_state(StatesGroup.{initial_state})
    fsm.import_transitions(
        storage=storage,
        states=StatesGroup.select(),
        triggers_funcs=(
            {handlers}
        )
    )
