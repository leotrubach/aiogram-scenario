from abc import ABC, abstractmethod
from typing import List, Optional

import aiogram

from .magazine import Magazine


class BaseStorage(aiogram.dispatcher.storage.BaseStorage, ABC):

    @abstractmethod
    async def set_magazine_states(self, *, chat: Optional[int] = None, user: Optional[int] = None,
                                  states: List[Optional[str]]) -> None:

        pass

    @abstractmethod
    async def get_magazine_states(self, *, chat: Optional[int] = None,
                                  user: Optional[int] = None) -> List[Optional[str]]:

        pass

    def get_magazine(self, *, chat: Optional[int] = None, user: Optional[int] = None) -> Magazine:

        chat_id, user_id = self.check_address(chat=chat, user=user)
        return Magazine(self, chat_id=chat_id, user_id=user_id)
