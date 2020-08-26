from typing import Union

from aiogram.contrib.fsm_storage import redis
from aiogram.utils import json

from aiogram_scenario.fsm.storages.base import BaseStorage


STATE_MAGAZINE_KEY = "magazine"


class RedisStorage(BaseStorage, redis.RedisStorage2):

    async def set_magazine(self, *, chat: Union[str, int, None] = None,
                           user: Union[str, int, None] = None,
                           states: list):

        chat, user = self.check_address(chat=chat, user=user)
        key = self.generate_key(chat, user, STATE_MAGAZINE_KEY)
        redis_ = await self.redis()
        await redis_.set(key, json.dumps(states), expire=self._state_ttl)

    async def get_magazine(self, *, chat: Union[str, int, None] = None,
                           user: Union[str, int, None] = None):

        chat, user = self.check_address(chat=chat, user=user)
        key = self.generate_key(chat, user, STATE_MAGAZINE_KEY)
        redis_ = await self.redis()
        raw_result = await redis_.get(key, encoding='utf8')
        if raw_result:
            return json.loads(raw_result)
        return []
