from abc import ABC, abstractmethod
from typing import Union

from aiogram.dispatcher import storage


class BaseStorage(storage.BaseStorage, ABC):

    async def reset_state(self, *,
                          chat: Union[str, int, None] = None,
                          user: Union[str, int, None] = None,
                          with_data: bool = True,
                          with_magazine: bool = True):

        await self.set_state(chat=chat, user=user, state=None)  # noqa
        if with_data:
            await self.set_data(chat=chat, user=user, data={})
        if with_magazine:
            await self.set_magazine(chat=chat, user=user, states=[])

    async def finish(self, *,
                     chat: Union[str, int, None] = None,
                     user: Union[str, int, None] = None):

        await self.reset_state(chat=chat, user=user, with_data=True, with_magazine=True)  # noqa

    @abstractmethod
    async def set_magazine(self, *, chat: Union[str, int, None] = None,
                           user: Union[str, int, None] = None,
                           states: list):

        pass

    @abstractmethod
    async def get_magazine(self, *, chat: Union[str, int, None] = None,
                           user: Union[str, int, None] = None):

        pass
