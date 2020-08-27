from typing import Union, List

from aiogram.contrib.fsm_storage import memory

from aiogram_scenario.fsm.storages.base import BaseStorage


class MemoryStorage(BaseStorage, memory.MemoryStorage):

    def resolve_address(self, chat, user):

        chat_id, user_id = map(str, self.check_address(chat=chat, user=user))
        if chat_id not in self.data:
            self.data[chat_id] = {}
        if user_id not in self.data[chat_id]:
            self.data[chat_id][user_id] = {"state": None, "data": {}, "bucket": {}, "magazine": []}

        return chat_id, user_id

    async def set_magazine(self, *, chat: Union[str, int, None] = None,
                           user: Union[str, int, None] = None,
                           states: list) -> None:

        chat, user = self.resolve_address(chat=chat, user=user)
        self.data[chat][user]["magazine"] = states.copy()

    async def get_magazine(self, *, chat: Union[str, int, None] = None,
                           user: Union[str, int, None] = None) -> List[str]:

        chat, user = self.resolve_address(chat=chat, user=user)
        return self.data[chat][user]["magazine"].copy()
