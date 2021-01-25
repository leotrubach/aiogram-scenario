from typing import Union, List, AnyStr, Optional

from aiogram.contrib.fsm_storage import memory

from .base import BaseStorage


class MemoryStorage(BaseStorage, memory.MemoryStorage):

    def resolve_address(self, chat, user):

        chat_id, user_id = self.check_address(chat=chat, user=user)
        if chat_id not in self.data:
            self.data[chat_id] = {}
        if user_id not in self.data[chat_id]:
            self.data[chat_id][user_id] = {"magazine": [None], "data": {}, "bucket": {}}

        return chat_id, user_id

    async def set_state(self, *, chat: Union[str, int, None] = None, user: Union[str, int, None] = None,
                        state: Optional[AnyStr] = None):
        chat, user = self.resolve_address(chat=chat, user=user)
        magazine = self.get_magazine(chat=chat, user=user)
        await magazine.load()
        await magazine.push(state)

    async def get_state(self, *, chat: Union[str, int, None] = None, user: Union[str, int, None] = None,
                        default: Optional[str] = None) -> Union[None, str]:

        chat, user = self.resolve_address(chat=chat, user=user)
        magazine = self.get_magazine(user=user, chat=chat)
        await magazine.load()

        return magazine.current_state

    async def set_magazine_states(self, *, chat: Optional[int] = None, user: Optional[int] = None,
                                  states: List[Union[None, str]]) -> None:

        chat, user = self.resolve_address(chat=chat, user=user)
        self.data[chat][user]["magazine"] = states.copy()

    async def get_magazine_states(self, *, chat: Optional[int] = None,
                                  user: Optional[int] = None) -> List[Optional[str]]:

        chat, user = self.resolve_address(chat=chat, user=user)
        return self.data[chat][user]["magazine"].copy()
