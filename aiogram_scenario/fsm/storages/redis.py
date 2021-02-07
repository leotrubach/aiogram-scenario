from typing import Union, List, Optional, AnyStr

from aiogram.contrib.fsm_storage import redis
from aiogram.utils import json

from .base import BaseStorage


STATE_MAGAZINE_KEY = "magazine"


class RedisStorage(BaseStorage, redis.RedisStorage2):

    async def set_state(self, *, chat: Union[str, int, None] = None, user: Union[str, int, None] = None,
                        state: Optional[AnyStr] = None):

        chat, user = self.check_address(chat=chat, user=user)
        magazine = self.get_magazine(chat=chat, user=user)
        await magazine.load()
        await magazine.push(state)

    async def get_state(self, *, chat: Union[str, int, None] = None, user: Union[str, int, None] = None,
                        default: Optional[str] = None) -> Optional[str]:

        chat, user = self.check_address(chat=chat, user=user)
        magazine = self.get_magazine(user=user, chat=chat)
        await magazine.load()
        return magazine.current_state

    async def set_magazine_states(self, *, chat: Optional[int] = None, user: Optional[int] = None,
                                  states: List[Optional[str]]) -> None:

        chat, user = self.check_address(chat=chat, user=user)
        key = self.generate_key(chat, user, STATE_MAGAZINE_KEY)
        redis_ = await self.redis()
        await redis_.set(key, json.dumps(states), expire=self._state_ttl)

    async def get_magazine_states(self, *, chat: Optional[int] = None,
                                  user: Optional[int] = None) -> List[Optional[str]]:

        chat, user = self.check_address(chat=chat, user=user)
        key = self.generate_key(chat, user, STATE_MAGAZINE_KEY)
        redis_ = await self.redis()
        raw_result = await redis_.get(key, encoding='utf8')
        if raw_result:
            return json.loads(raw_result)

        return [None]
