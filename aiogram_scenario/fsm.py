from typing import Optional
import logging

from aiogram import Dispatcher
from aiogram.dispatcher.storage import BaseStorage
from aiogram.dispatcher.handler import current_handler, ctx_data
from aiogram.types import Update

from .state import AbstractState
from .states_map import StatesMap
from . import utils


logger = logging.getLogger(__name__)


def _get_current_update():

    update = Update.get_current()

    for update_type_attr in ("message", "edited_message", "channel_post", "edited_channel_post", "inline_query",
                             "chosen_inline_result", "callback_query", "shipping_query", "pre_checkout_query",
                             "poll", "poll_answer"):
        update_type_obj = getattr(update, update_type_attr)
        if update_type_obj is not None:
            return update_type_obj


class StatesStack:

    def __init__(self, storage: BaseStorage, user_id: Optional[int] = None, chat_id: Optional[int] = None):

        self._storage = storage
        self._user_id = user_id
        self._chat_id = chat_id

    async def push(self, state: str) -> None:

        data = await self._get_data()
        try:
            stack: list = data["states_stack"]
        except KeyError:
            data["states_stack"] = stack = []

        try:
            state_index = stack.index(state)
        except ValueError:  # not on the stack
            stack.append(state)
        else:  # exists on the stack
            del stack[state_index:]

        await self._update_data(data)
        logger.debug(f"Pushed onto the stack (user_id={self._user_id}, chat_id={self._chat_id}): {stack}")

    async def pop(self) -> str:

        data = await self._get_data()
        stack: list = data["states_stack"]

        self._pop(stack)
        state = stack[-1]
        await self._update_data(data)
        logger.debug(f"Removed from the stack (user_id={self._user_id}, chat_id={self._chat_id}): {stack}")

        return state

    @staticmethod
    def _pop(stack: list) -> str:

        try:
            state: str = stack.pop()
        except IndexError:
            raise IndexError("stack is empty")

        return state

    async def clear(self):

        await self._storage.reset_data(chat=self._chat_id, user=self._user_id)

    async def _get_data(self):

        return await self._storage.get_data(chat=self._chat_id, user=self._user_id)

    async def _update_data(self, data):

        await self._storage.update_data(chat=self._chat_id, user=self._user_id, data=data)


class FSM:

    def __init__(self, stack_storage: BaseStorage, states_map: StatesMap, dispatcher: Dispatcher):

        self._stack_storage = stack_storage
        self._states_map = states_map
        self._dispatcher = dispatcher

    async def execute_next_transition(self, user_id: Optional[int] = None, chat_id: Optional[int] = None,
                                      conditions: Optional[dict] = None):

        if conditions is None:
            conditions = {}

        logger.debug(f"Executing next transition (user_id={user_id}, chat_id={chat_id})...")
        pointing_handler = current_handler.get()
        target_state = self._states_map.get_state_by_handler(pointing_handler, conditions=conditions)
        stack = await self._get_states_stack(user_id, chat_id)

        serialized_state = self._serialize_state(target_state)

        await stack.push(state=serialized_state)
        await self._execute_transition(state=target_state, user_id=user_id, chat_id=chat_id)

    async def execute_back_transition(self, user_id: Optional[int] = None, chat_id: Optional[int] = None):

        logger.debug(f"Executing back transition (user_id={user_id}, chat_id={chat_id})...")
        stack = await self._get_states_stack(user_id=user_id, chat_id=chat_id)
        serialized_state = await stack.pop()

        state = self._deserialize_state(state=serialized_state)

        await self._execute_transition(state=state, user_id=user_id, chat_id=chat_id)

    @staticmethod
    def _serialize_state(state: AbstractState) -> str:

        return state.name

    def _deserialize_state(self, state: str) -> AbstractState:

        return self._states_map.get_state_by_name(state_name=state)

    async def _execute_transition(self, state: AbstractState, user_id: Optional[int] = None,
                                  chat_id: Optional[int] = None):

        update = _get_current_update()
        context_data = ctx_data.get()
        fsm_context = self._dispatcher.current_state(chat=chat_id, user=user_id)

        handler_args = (update,)
        context_kwargs = utils.get_existing_kwargs(state.process_transition, check_varkw=True, **context_data)

        await fsm_context.set_state(state.name)
        await state.process_transition(*handler_args, **context_kwargs)
        logger.debug(f"Transition to '{state}' completed (user_id={user_id}, chat_id={chat_id}).")

    async def _get_states_stack(self, user_id: int, chat_id: Optional[int] = None):

        return StatesStack(storage=self._stack_storage, user_id=user_id, chat_id=chat_id)


class FSMPointer:

    def __init__(self, fsm: FSM, user_id: Optional[int] = None, chat_id: Optional[int] = None):

        self._fsm = fsm
        self._chat_id = chat_id
        self._user_id = user_id

    async def go_next(self, **conditions):

        await self._fsm.execute_next_transition(chat_id=self._chat_id, user_id=self._user_id, conditions=conditions)

    async def go_back(self):

        await self._fsm.execute_back_transition(chat_id=self._chat_id, user_id=self._user_id)
