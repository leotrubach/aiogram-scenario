from .base import AbstractLocksStorage


class MemoryLocksStorage(AbstractLocksStorage):

    def __init__(self):

        self._locks = {}

    async def check(self, *, chat_id: int, user_id: int) -> bool:

        try:
            return user_id in self._locks[chat_id]
        except KeyError:
            return False

    async def set(self, *, chat_id: int, user_id: int) -> None:

        try:
            self._locks[chat_id].add(user_id)
        except KeyError:
            self._locks[chat_id] = {user_id}

    async def unset(self, *, chat_id: int, user_id: int) -> None:

        chat_users_ids: set = self._locks[chat_id]
        chat_users_ids.remove(user_id)
        if not chat_users_ids:
            del self._locks[chat_id]
