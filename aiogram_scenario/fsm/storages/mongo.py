from typing import Union, List, Optional, AnyStr

from aiogram.contrib.fsm_storage import mongo
from aiogram.contrib.fsm_storage.mongo import DATA, BUCKET

from .base import BaseStorage


MAGAZINE = "aiogram_magazine"
COLLECTIONS = (MAGAZINE, DATA, BUCKET)


class MongoStorage(BaseStorage, mongo.MongoStorage):

    async def set_state(self, *, chat: Union[str, int, None] = None,
                        user: Union[str, int, None] = None,
                        state: Optional[AnyStr] = None):

        chat, user = self.check_address(chat=chat, user=user)
        magazine = self.get_magazine(user=user, chat=chat)
        await magazine.load()
        await magazine.push(state)

    async def get_state(self, *, chat: Union[str, int, None] = None,
                        user: Union[str, int, None] = None,
                        default: Optional[str] = None) -> Optional[str]:

        chat, user = self.check_address(chat=chat, user=user)
        magazine = self.get_magazine(user=user, chat=chat)
        await magazine.load()

        return magazine.current_state

    async def set_magazine_states(self, *, chat: Optional[int] = None,
                                  user: Optional[int] = None,
                                  states: List[Union[None, str]]) -> None:

        chat, user = self.check_address(chat=chat, user=user)
        db = await self.get_db()
        await db[MAGAZINE].update_one(filter={'chat': chat, 'user': user},
                                      update={'$set': {'magazine': states}}, upsert=True)

    async def get_magazine_states(self, *, chat: Optional[int] = None,
                                  user: Optional[int] = None) -> List[Optional[str]]:

        chat, user = self.check_address(chat=chat, user=user)
        db = await self.get_db()
        result = await db[MAGAZINE].find_one(filter={'chat': chat, 'user': user})
        return result.get('magazine') if result else [None]

    async def reset_all(self, full=True):

        db = await self.get_db()

        await db[MAGAZINE].drop()

        if full:
            await db[DATA].drop()
            await db[BUCKET].drop()

    @staticmethod
    async def apply_index(db):

        for collection in COLLECTIONS:
            await db[collection].create_index(keys=[('chat', 1), ('user', 1)],
                                              name="chat_user_idx", unique=True, background=True)
