from typing import Any
from contextvars import ContextVar

from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware

from aiogramscenario.scenario.machine import ScenarioMachine
from aiogramscenario.scenario.context_machine import ScenarioMachineContext, ContextData
from aiogramscenario import helpers


chat_id_context = ContextVar("chat_id_context")
user_id_context = ContextVar("user_id_context")
event_context = ContextVar("event_context")
handler_context = ContextVar("handler_context")


class ScenarioMiddleware(BaseMiddleware):

    def __init__(self, machine: ScenarioMachine, scene_data: Any = None, *, arg_name: str = "machine"):

        super().__init__()
        context_data = ContextData(chat_id=chat_id_context, user_id=user_id_context,
                                   handler=handler_context, event=event_context)
        self._machine = ScenarioMachineContext(machine, context_data, scene_data)
        self._arg_name = arg_name

    async def _on_process(self, event, data: dict) -> None:

        chat_id_context.set(helpers.get_chat_id_with_context())
        user_id_context.set(helpers.get_user_id_with_context())
        handler_context.set(helpers.get_handler_with_context())
        event_context.set(event)

        data[self._arg_name] = self._machine

    on_process_message = _on_process

    on_process_callback_query = _on_process

    on_process_edited_message = _on_process

    on_process_channel_post = _on_process

    on_process_edited_channel_post = _on_process


def setup_scenario_middleware(dispatcher: Dispatcher, machine: ScenarioMachine,
                              scene_data: Any = None, *, arg_name: str = "machine") -> None:

    middleware = ScenarioMiddleware(machine, scene_data, arg_name=arg_name)
    dispatcher.setup_middleware(middleware)
