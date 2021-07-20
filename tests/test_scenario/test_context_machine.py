from contextvars import ContextVar
from unittest.mock import AsyncMock
import asyncio

import pytest
from tgbotscenario import errors
import tgbotscenario.errors.scenario_machine

from aiogramscenario import ScenarioMachine, ScenarioMachineContext, ContextData, BaseScene
from aiogramscenario.scenario.storages.states.memory import MemoryStateStorage


chat_id_context = ContextVar("chat_id_context")
user_id_context = ContextVar("user_id_context")
handler_context = ContextVar("handler_context")
event_context = ContextVar("event_context")


@pytest.fixture()
def context_data(chat_id, user_id, handler, event_stub):

    data = ContextData(chat_id=chat_id_context, user_id=user_id_context, handler=handler_context, event=event_context)

    chat_id_token = chat_id_context.set(chat_id)
    user_id_token = user_id_context.set(user_id)
    handler_token = handler_context.set(handler)
    event_token = event_context.set(event_stub)

    yield data

    chat_id_context.reset(chat_id_token)
    user_id_context.reset(user_id_token)
    handler_context.reset(handler_token)
    event_context.reset(event_token)


class TestScenarioMachineContextMoveToNextScene:

    @pytest.mark.asyncio
    async def test(self, chat_id, user_id, context_data, event_stub, scene_data_stub, handler):

        class InitialScene(BaseScene):
            pass

        class FooScene(BaseScene):
            pass

        initial_scene_mock = AsyncMock(InitialScene)
        foo_scene_mock = AsyncMock(FooScene)
        foo_scene_mock.name = "FooScene"
        machine = ScenarioMachine(initial_scene_mock, MemoryStateStorage())
        machine.add_transition(initial_scene_mock, foo_scene_mock, handler)
        context_machine = ScenarioMachineContext(machine, context_data, scene_data_stub)
        await context_machine.move_to_next_scene()
        current_scene = await machine.get_current_scene(chat_id=chat_id, user_id=user_id)
        current_state = await machine.get_current_state(chat_id=chat_id, user_id=user_id)

        initial_scene_mock.process_exit.assert_awaited_once_with(event_stub, scene_data_stub)
        foo_scene_mock.process_enter.assert_awaited_once_with(event_stub, scene_data_stub)
        assert current_scene is foo_scene_mock
        assert current_state == "FooScene"

    @pytest.mark.asyncio
    async def test_transition_not_exists(self, context_data, scene_data_stub):

        class InitialScene(BaseScene):
            pass

        initial_scene = InitialScene()
        machine = ScenarioMachine(initial_scene, MemoryStateStorage())
        context_machine = ScenarioMachineContext(machine, context_data, scene_data_stub)

        with pytest.raises(errors.scenario_machine.NextTransitionNotFoundError):
            await context_machine.move_to_next_scene()

    @pytest.mark.asyncio
    async def test_concurrent_transitions(self, chat_id, user_id, context_data, event_stub,
                                          scene_data_stub, handler):

        class InitialScene(BaseScene):
            pass

        class FooScene(BaseScene):
            pass

        # noinspection PyUnusedLocal
        async def fake_process(event, data):
            await asyncio.sleep(0.1)

        initial_scene_mock = AsyncMock(InitialScene)
        initial_scene_mock.process_exit.side_effect = fake_process
        foo_scene_mock = AsyncMock(FooScene)
        foo_scene_mock.name = "FooScene"
        foo_scene_mock.process_enter.side_effect = fake_process

        machine = ScenarioMachine(initial_scene_mock, MemoryStateStorage())
        machine.add_transition(initial_scene_mock, foo_scene_mock, handler)
        context_machine = ScenarioMachineContext(machine, context_data, scene_data_stub)
        first_task = asyncio.create_task(machine.execute_next_transition(
            chat_id=chat_id, user_id=user_id, scene_args=(event_stub, scene_data_stub), handler=handler)
        )
        await asyncio.sleep(0)  # to start the first task before the second

        with pytest.raises(errors.scenario_machine.TransitionLockedError):
            await context_machine.move_to_next_scene()

        await first_task
        current_scene = await machine.get_current_scene(chat_id=chat_id, user_id=user_id)
        current_state = await machine.get_current_state(chat_id=chat_id, user_id=user_id)

        initial_scene_mock.process_exit.assert_awaited_once_with(event_stub, scene_data_stub)
        foo_scene_mock.process_enter.assert_awaited_once_with(event_stub, scene_data_stub)
        assert current_scene is foo_scene_mock
        assert current_state == "FooScene"

    @pytest.mark.asyncio
    async def test_suppress_lock_error(self, chat_id, user_id, context_data, event_stub,
                                       scene_data_stub, handler):

        class InitialScene(BaseScene):
            pass

        class FooScene(BaseScene):
            pass

        # noinspection PyUnusedLocal
        async def fake_process(event, data):
            await asyncio.sleep(0.1)

        initial_scene_mock = AsyncMock(InitialScene)
        initial_scene_mock.process_exit.side_effect = fake_process
        foo_scene_mock = AsyncMock(FooScene)
        foo_scene_mock.name = "FooScene"
        foo_scene_mock.process_enter.side_effect = fake_process
        machine = ScenarioMachine(initial_scene_mock, MemoryStateStorage(), suppress_lock_error=True)
        machine.add_transition(initial_scene_mock, foo_scene_mock, handler)
        context_machine = ScenarioMachineContext(machine, context_data, scene_data_stub)
        await asyncio.gather(
            machine.execute_next_transition(
                chat_id=chat_id, user_id=user_id, scene_args=(event_stub, scene_data_stub),
                handler=handler
            ),
            context_machine.move_to_next_scene()
        )
        current_scene = await machine.get_current_scene(chat_id=chat_id, user_id=user_id)
        current_state = await machine.get_current_state(chat_id=chat_id, user_id=user_id)

        initial_scene_mock.process_exit.assert_awaited_once_with(event_stub, scene_data_stub)
        foo_scene_mock.process_enter.assert_awaited_once_with(event_stub, scene_data_stub)
        assert current_scene is foo_scene_mock
        assert current_state == "FooScene"


class TestScenarioMachineContextMoveToPreviousScene:

    @pytest.mark.asyncio
    async def test(self, chat_id, user_id, context_data, event_stub, handler, scene_data_stub):

        class InitialScene(BaseScene):
            pass

        class FooScene(BaseScene):
            pass

        initial_scene_mock = AsyncMock(InitialScene)
        initial_scene_mock.name = "InitialScene"
        foo_scene_mock = AsyncMock(FooScene)
        machine = ScenarioMachine(initial_scene_mock, MemoryStateStorage())
        machine.add_transition(initial_scene_mock, foo_scene_mock, handler)
        context_machine = ScenarioMachineContext(machine, context_data, scene_data_stub)
        await machine.execute_next_transition(chat_id=chat_id, user_id=user_id,
                                              scene_args=(event_stub, scene_data_stub), handler=handler)
        await context_machine.move_to_previous_scene()

        current_scene = await machine.get_current_scene(chat_id=chat_id, user_id=user_id)
        current_state = await machine.get_current_state(chat_id=chat_id, user_id=user_id)

        foo_scene_mock.process_exit.assert_awaited_once_with(event_stub, scene_data_stub)
        initial_scene_mock.process_enter.assert_awaited_once_with(event_stub, scene_data_stub)
        assert current_scene is initial_scene_mock
        assert current_state == "InitialScene"

    @pytest.mark.asyncio
    async def test_previous_state_not_exists(self, scene_data_stub, context_data):

        class InitialScene(BaseScene):
            pass

        initial_scene = InitialScene()
        machine = ScenarioMachine(initial_scene, MemoryStateStorage())
        context_machine = ScenarioMachineContext(machine, context_data, scene_data_stub)

        with pytest.raises(errors.scenario_machine.BackTransitionNotFoundError):
            await context_machine.move_to_previous_scene()

    @pytest.mark.asyncio
    async def test_concurrent_transitions(self, chat_id, user_id, context_data, event_stub,
                                          scene_data_stub, handler):

        class InitialScene(BaseScene):
            pass

        class FooScene(BaseScene):
            pass

        # noinspection PyUnusedLocal
        async def fake_process(event, data):
            await asyncio.sleep(0.1)

        initial_scene_mock = AsyncMock(InitialScene)
        initial_scene_mock.name = "InitialScene"
        initial_scene_mock.process_enter.side_effect = fake_process
        foo_scene_mock = AsyncMock(FooScene)
        foo_scene_mock.process_exit.side_effect = fake_process

        machine = ScenarioMachine(initial_scene_mock, MemoryStateStorage())
        machine.add_transition(initial_scene_mock, foo_scene_mock, handler)
        context_machine = ScenarioMachineContext(machine, context_data, scene_data_stub)
        await machine.execute_next_transition(chat_id=chat_id, user_id=user_id,
                                              scene_args=(event_stub, scene_data_stub), handler=handler)
        first_task = asyncio.create_task(machine.execute_back_transition(
            chat_id=chat_id, user_id=user_id, scene_args=(event_stub, scene_data_stub))
        )
        await asyncio.sleep(0)  # to start the first task before the second

        with pytest.raises(errors.scenario_machine.TransitionLockedError):
            await context_machine.move_to_previous_scene()

        await first_task
        current_scene = await machine.get_current_scene(chat_id=chat_id, user_id=user_id)
        current_state = await machine.get_current_state(chat_id=chat_id, user_id=user_id)

        foo_scene_mock.process_exit.assert_awaited_once_with(event_stub, scene_data_stub)
        initial_scene_mock.process_enter.assert_awaited_once_with(event_stub, scene_data_stub)
        assert current_scene is initial_scene_mock
        assert current_state == "InitialScene"

    @pytest.mark.asyncio
    async def test_suppress_lock_error(self, chat_id, user_id, context_data, event_stub,
                                       scene_data_stub, handler):

        class InitialScene(BaseScene):
            pass

        class FooScene(BaseScene):
            pass

        # noinspection PyUnusedLocal
        async def fake_process(event, data):
            await asyncio.sleep(0.1)

        initial_scene_mock = AsyncMock(InitialScene)
        initial_scene_mock.name = "InitialScene"
        initial_scene_mock.process_exit.side_effect = fake_process
        foo_scene_mock = AsyncMock(FooScene)
        foo_scene_mock.process_exit.side_effect = fake_process
        foo_scene_mock.process_enter.side_effect = fake_process
        machine = ScenarioMachine(initial_scene_mock, MemoryStateStorage(), suppress_lock_error=True)
        machine.add_transition(initial_scene_mock, foo_scene_mock, handler)
        context_machine = ScenarioMachineContext(machine, context_data, scene_data_stub)
        await machine.execute_next_transition(chat_id=chat_id, user_id=user_id,
                                              scene_args=(event_stub, scene_data_stub), handler=handler)
        await asyncio.gather(
            machine.execute_back_transition(chat_id=chat_id, user_id=user_id,
                                            scene_args=(event_stub, scene_data_stub)),
            context_machine.move_to_previous_scene()
        )
        current_scene = await machine.get_current_scene(chat_id=chat_id, user_id=user_id)
        current_state = await machine.get_current_state(chat_id=chat_id, user_id=user_id)

        foo_scene_mock.process_exit.assert_awaited_once_with(event_stub, scene_data_stub)
        initial_scene_mock.process_enter.assert_awaited_once_with(event_stub, scene_data_stub)
        assert current_scene is initial_scene_mock
        assert current_state == "InitialScene"


class TestScenarioMachineContextRefreshScene:

    @pytest.mark.asyncio
    async def test(self, chat_id, user_id, event_stub, context_data, scene_data_stub):

        class InitialScene(BaseScene):
            pass

        initial_scene_mock = AsyncMock(InitialScene)
        initial_scene_mock.name = "InitialScene"
        machine = ScenarioMachine(initial_scene_mock, MemoryStateStorage())
        context_machine = ScenarioMachineContext(machine, context_data, scene_data_stub)
        await context_machine.refresh_scene()
        current_scene = await machine.get_current_scene(chat_id=chat_id, user_id=user_id)
        current_state = await machine.get_current_state(chat_id=chat_id, user_id=user_id)

        initial_scene_mock.process_enter.assert_awaited_once_with(event_stub, scene_data_stub)
        assert current_scene is initial_scene_mock
        assert current_state == "InitialScene"
