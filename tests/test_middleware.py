import pytest
from aiogram import Bot, Dispatcher

from aiogramscenario import (ScenarioMiddleware, ScenarioMachine, BaseScene,
                             ScenarioMachineContext, setup_scenario_middleware)
from aiogramscenario.scenario.storages.states.memory import MemoryStateStorage
from aiogramscenario.middleware import chat_id_context, user_id_context, event_context, handler_context


class TestScenarioMiddlewareOnProcessMessage:

    @pytest.mark.asyncio
    async def test(self, event_stub, chat, user, handler):

        class InitialScene(BaseScene):
            pass

        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        middleware = ScenarioMiddleware(machine)
        data = {}
        await middleware.on_process_message(event_stub, data)

        assert chat_id_context.get() == chat.id
        assert user_id_context.get() == user.id
        assert handler_context.get() == handler
        assert event_context.get() == event_stub
        assert "machine" in data
        assert isinstance(data["machine"], ScenarioMachineContext)

    @pytest.mark.asyncio
    async def test_another_arg_name(self, event_stub, chat, user, handler):

        class InitialScene(BaseScene):
            pass

        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        middleware = ScenarioMiddleware(machine, arg_name="somearg")
        data = {}
        await middleware.on_process_message(event_stub, data)

        assert chat_id_context.get() == chat.id
        assert user_id_context.get() == user.id
        assert handler_context.get() == handler
        assert event_context.get() == event_stub
        assert "somearg" in data
        assert isinstance(data["somearg"], ScenarioMachineContext)


class TestScenarioMiddlewareOnProcessCallbackQuery:

    @pytest.mark.asyncio
    async def test(self, event_stub, chat, user, handler):

        class InitialScene(BaseScene):
            pass

        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        middleware = ScenarioMiddleware(machine)
        data = {}
        await middleware.on_process_callback_query(event_stub, data)

        assert chat_id_context.get() == chat.id
        assert user_id_context.get() == user.id
        assert handler_context.get() == handler
        assert event_context.get() == event_stub
        assert "machine" in data
        assert isinstance(data["machine"], ScenarioMachineContext)

    @pytest.mark.asyncio
    async def test_another_arg_name(self, event_stub, chat, user, handler):

        class InitialScene(BaseScene):
            pass

        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        middleware = ScenarioMiddleware(machine, arg_name="somearg")
        data = {}
        await middleware.on_process_callback_query(event_stub, data)

        assert chat_id_context.get() == chat.id
        assert user_id_context.get() == user.id
        assert handler_context.get() == handler
        assert event_context.get() == event_stub
        assert "somearg" in data
        assert isinstance(data["somearg"], ScenarioMachineContext)


class TestScenarioMiddlewareOnProcessEditedMessage:

    @pytest.mark.asyncio
    async def test(self, event_stub, chat, user, handler):

        class InitialScene(BaseScene):
            pass

        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        middleware = ScenarioMiddleware(machine)
        data = {}
        await middleware.on_process_edited_message(event_stub, data)

        assert chat_id_context.get() == chat.id
        assert user_id_context.get() == user.id
        assert handler_context.get() == handler
        assert event_context.get() == event_stub
        assert "machine" in data
        assert isinstance(data["machine"], ScenarioMachineContext)

    @pytest.mark.asyncio
    async def test_another_arg_name(self, event_stub, chat, user, handler):

        class InitialScene(BaseScene):
            pass

        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        middleware = ScenarioMiddleware(machine, arg_name="somearg")
        data = {}
        await middleware.on_process_edited_message(event_stub, data)

        assert chat_id_context.get() == chat.id
        assert user_id_context.get() == user.id
        assert handler_context.get() == handler
        assert event_context.get() == event_stub
        assert "somearg" in data
        assert isinstance(data["somearg"], ScenarioMachineContext)


class TestScenarioMiddlewareOnProcessChannelPost:

    @pytest.mark.asyncio
    async def test(self, event_stub, chat, user, handler):

        class InitialScene(BaseScene):
            pass

        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        middleware = ScenarioMiddleware(machine)
        data = {}
        await middleware.on_process_channel_post(event_stub, data)

        assert chat_id_context.get() == chat.id
        assert user_id_context.get() == user.id
        assert handler_context.get() == handler
        assert event_context.get() == event_stub
        assert "machine" in data
        assert isinstance(data["machine"], ScenarioMachineContext)

    @pytest.mark.asyncio
    async def test_another_arg_name(self, event_stub, chat, user, handler):

        class InitialScene(BaseScene):
            pass

        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        middleware = ScenarioMiddleware(machine, arg_name="somearg")
        data = {}
        await middleware.on_process_channel_post(event_stub, data)

        assert chat_id_context.get() == chat.id
        assert user_id_context.get() == user.id
        assert handler_context.get() == handler
        assert event_context.get() == event_stub
        assert "somearg" in data
        assert isinstance(data["somearg"], ScenarioMachineContext)


class TestScenarioMiddlewareOnProcessEditedChannelPost:

    @pytest.mark.asyncio
    async def test(self, event_stub, chat, user, handler):

        class InitialScene(BaseScene):
            pass

        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        middleware = ScenarioMiddleware(machine)
        data = {}
        await middleware.on_process_edited_channel_post(event_stub, data)

        assert chat_id_context.get() == chat.id
        assert user_id_context.get() == user.id
        assert handler_context.get() == handler
        assert event_context.get() == event_stub
        assert "machine" in data
        assert isinstance(data["machine"], ScenarioMachineContext)

    @pytest.mark.asyncio
    async def test_another_arg_name(self, event_stub, chat, user, handler):

        class InitialScene(BaseScene):
            pass

        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        middleware = ScenarioMiddleware(machine, arg_name="somearg")
        data = {}
        await middleware.on_process_edited_channel_post(event_stub, data)

        assert chat_id_context.get() == chat.id
        assert user_id_context.get() == user.id
        assert handler_context.get() == handler
        assert event_context.get() == event_stub
        assert "somearg" in data
        assert isinstance(data["somearg"], ScenarioMachineContext)


class TestSetupScenarioMiddleware:

    def test(self):

        class InitialScene(BaseScene):
            pass

        dispatcher = Dispatcher(Bot("123:abc"))
        machine = ScenarioMachine(InitialScene(), MemoryStateStorage())
        setup_scenario_middleware(dispatcher, machine)

        assert any(isinstance(i, ScenarioMiddleware) for i in dispatcher.middleware.applications)
