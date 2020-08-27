from typing import Union, List

from aiogram.contrib.fsm_storage import mongo
from aiogram.contrib.fsm_storage.mongo import STATE, DATA, BUCKET

from aiogram_scenario.fsm.storages.base import BaseStorage


MAGAZINE = "aiogram_magazine"
COLLECTIONS = (STATE, DATA, BUCKET, MAGAZINE)


class MongoStorage(BaseStorage, mongo.MongoStorage):

    async def set_magazine(self, *, chat: Union[str, int, None] = None,
                           user: Union[str, int, None] = None,
                           states: list) -> None:

        chat, user = self.check_address(chat=chat, user=user)
        db = await self.get_db()

        await db[MAGAZINE].update_one(filter={'chat': chat, 'user': user},
                                      update={'$set': {'magazine': states}}, upsert=True)

    async def get_magazine(self, *, chat: Union[str, int, None] = None,
                           user: Union[str, int, None] = None) -> List[str]:

        chat, user = self.check_address(chat=chat, user=user)
        db = await self.get_db()
        result = await db[MAGAZINE].find_one(filter={'chat': chat, 'user': user})

        return result.get('magazine') if result else []

    async def reset_all(self, full=True):

        db = await self.get_db()

        await db[STATE].drop()

        if full:
            await db[DATA].drop()
            await db[BUCKET].drop()
            await db[MAGAZINE].drop()

    @staticmethod
    async def apply_index(db):

        for collection in COLLECTIONS:
            await db[collection].create_index(keys=[('chat', 1), ('user', 1)],
                                              name="chat_user_idx", unique=True, background=True)
