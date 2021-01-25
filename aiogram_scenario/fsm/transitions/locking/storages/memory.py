from .base import AbstractLocksStorage


class MemoryLocksStorage(AbstractLocksStorage):

    def __init__(self):

        self._locks = {}

    async def check_locking(self, *, chat_id: int, user_id: int) -> bool:

        try:
            return user_id in self._locks[chat_id]
        except KeyError:
            return False

    async def set_lock(self, *, chat_id: int, user_id: int) -> None:

        try:
            self._locks[chat_id].add(user_id)
        except KeyError:
            self._locks[chat_id] = {user_id}

    async def unset_lock(self, *, chat_id: int, user_id: int) -> None:

        chat_users_ids: set = self._locks[chat_id]
        if len(chat_users_ids) > 1:
            chat_users_ids.remove(user_id)
        else:
            del self._locks[chat_id]
