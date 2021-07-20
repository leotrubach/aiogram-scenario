from unittest.mock import AsyncMock

import pytest
from aiogram import Bot, Dispatcher

from aiogramscenario import SceneFilter, BaseScene, ScenarioMachine, setup_scene_filter
from aiogramscenario.scenario.storages.states.memory import MemoryStateStorage
from aiogramscenario.filter import machine_context


class TestSceneFilterCheck:

    @pytest.mark.asyncio
    async def test_scene_fits(self, event_stub, chat, user):

        class InitialScene(BaseScene):
            pass

        initial_scene = InitialScene()
        machine = ScenarioMachine(initial_scene, MemoryStateStorage())
        machine_context.set(machine)
        filter_ = SceneFilter(initial_scene)

        assert await filter_.check(event_stub) is True

    @pytest.mark.asyncio
    async def test_scene_not_fits(self, event_stub, chat, user, handler, scene_data_stub):

        class InitialScene(BaseScene):
            pass

        class FooScene(BaseScene):
            pass

        initial_scene = InitialScene()
        foo_scene = FooScene()
        machine = ScenarioMachine(initial_scene, MemoryStateStorage())
        machine.add_transition(initial_scene, foo_scene, handler)
        await machine.execute_next_transition(chat_id=chat.id, user_id=user.id,
                                              scene_args=(event_stub, scene_data_stub), handler=handler)
        machine_context.set(machine)
        filter_ = SceneFilter(initial_scene)

        assert await filter_.check(event_stub) is False

    @pytest.mark.asyncio
    async def test_caching(self, event_stub, chat, user):

        class InitialScene(BaseScene):
            pass

        initial_scene = InitialScene()
        machine = ScenarioMachine(initial_scene, MemoryStateStorage())
        machine_mock = AsyncMock(machine)
        machine_mock.get_current_scene.side_effect = machine.get_current_scene
        machine_context.set(machine_mock)
        filter_ = SceneFilter(initial_scene)
        for _ in range(3):
            await filter_.check(event_stub)

        machine_mock.get_current_scene.assert_awaited_once_with(chat_id=chat.id, user_id=user.id)


class TestSetupSceneFilter:

    def test(self):

        class InitialScene(BaseScene):
            pass

        dispatcher = Dispatcher(Bot("123:abc"))
        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        setup_scene_filter(dispatcher, machine)

        assert SceneFilter in (record.callback for record in dispatcher.filters_factory._registered)
