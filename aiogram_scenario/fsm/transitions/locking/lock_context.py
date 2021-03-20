from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .storages.base import AbstractLockingStorage


class LockContext:

    __slots__ = ("_storage", "_chat_id", "_user_id")

    def __init__(self, storage: "AbstractLockingStorage", *, chat_id: int, user_id: int):

        self._storage = storage
        self._chat_id = chat_id
        self._user_id = user_id

    async def __aenter__(self):

        await self._storage.add(chat_id=self._chat_id, user_id=self._user_id)

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        await self._storage.remove(chat_id=self._chat_id, user_id=self._user_id)
