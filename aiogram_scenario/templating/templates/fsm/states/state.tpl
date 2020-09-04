from aiogram_scenario import AbstractState, FSMTrigger
from aiogram.types import ...  # select event types (or remove the line)


{handlers}


class {state_name}(AbstractState):

    async def process_enter(self, event, **kwargs) -> None:
        ...  # define here logic for entering this state (also you can remove the method)

    async def process_exit(self, event, **kwargs) -> None:
        ...  # define here logic for exiting this state (also you can remove the method)

    def register_handlers(self, registrar: Registrar, **reg_kwargs) -> None:
        ...  # register handlers for this state here with the registrar
