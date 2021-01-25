from typing import Optional

from .storages import AbstractLocksStorage
from .lock_data import LockData
from aiogram_scenario.fsm.state import BaseState


class LockContext:

    __slots__ = ("_storage", "_source_state", "_destination_state", "_chat_id", "_user_id", "_lock_data")

    def __init__(self, storage: AbstractLocksStorage, source_state: BaseState,
                 destination_state: BaseState, chat_id: int, user_id: int):

        self._storage = storage
        self._source_state = source_state
        self._destination_state = destination_state
        self._chat_id = chat_id
        self._user_id = user_id
        self._lock_data: Optional[LockData] = None

    async def __aenter__(self):

        self._lock_data = await self._storage.add_lock(
            source_state=self._source_state,
            destination_state=self._destination_state,
            chat_id=self._chat_id,
            user_id=self._user_id
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        await self._storage.remove_lock(self._lock_data)
