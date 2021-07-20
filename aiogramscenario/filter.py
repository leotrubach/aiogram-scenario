from contextvars import ContextVar

from aiogram.dispatcher.filters import BoundFilter
from aiogram import Dispatcher
from aiogram.dispatcher.filters import StateFilter

from aiogramscenario.scenario.machine import ScenarioMachine
from aiogramscenario.scenario.scene import BaseScene
from aiogramscenario import helpers


machine_context = ContextVar("machine_context")
scene_cache_context = ContextVar("scene_cache_context")


class SceneFilter(BoundFilter):

    key = "scene"
    required = True

    def __init__(self, scene: BaseScene):

        self._scene = scene

        # due to peculiarities of initializing filters in aiogram
        self._machine: ScenarioMachine = machine_context.get()

    async def check(self, event) -> bool:

        try:
            scene = scene_cache_context.get()
        except LookupError:
            chat_id = helpers.get_chat_id_with_context()
            user_id = helpers.get_user_id_with_context()
            scene = await self._machine.get_current_scene(chat_id=chat_id, user_id=user_id)
            scene_cache_context.set(scene)

        return scene is self._scene


def setup_scene_filter(dispatcher: Dispatcher, machine: ScenarioMachine) -> None:

    machine_context.set(machine)
    dispatcher.unbind_filter(StateFilter)
    dispatcher.bind_filter(SceneFilter, event_handlers=[
        dispatcher.message_handlers,
        dispatcher.callback_query_handlers,
        dispatcher.edited_message_handlers,
        dispatcher.channel_post_handlers,
        dispatcher.edited_channel_post_handlers
    ])
