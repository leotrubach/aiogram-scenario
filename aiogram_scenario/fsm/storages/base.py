from abc import ABC, abstractmethod
from typing import Union, List, Optional
import logging

import aiogram

from aiogram_scenario import exceptions


logger = logging.getLogger(__name__)


class Magazine:

    def __init__(self, storage: "BaseStorage", *,
                 user_id: Optional[int] = None,
                 chat_id: Optional[int] = None):

        if chat_id is None and user_id is None:
            raise ValueError(f"at least one parameter must be specified ({user_id=}, {chat_id=})!")

        self._storage = storage
        self._user_id = user_id
        self._chat_id = chat_id
        self._states: Optional[List[Optional[str]]] = None

    def __str__(self):

        class_part = self.__class__.__name__
        try:
            return f"<{class_part} {self.states}>"
        except exceptions.magazine.MagazineIsNotLoadedError:
            return f"<{class_part} NOT LOADED!>"

    __repr__ = __str__

    async def load(self) -> None:

        self._states = await self._storage.get_magazine_states(chat=self._chat_id, user=self._user_id)

        logger.debug(f"States loaded into the magazine: {self._states}, "
                     f"(user_id={self._user_id}, chat_id={self._chat_id})!")

    def set(self, state: Optional[str]) -> None:

        try:
            state_index = self.states.index(state)
        except ValueError:  # not on the magazine
            self._states.append(state)
        else:  # exists on the magazine
            del self._states[state_index + 1:]

        logger.debug(f"Magazine set state: '{state}' (user_id={self._user_id}, chat_id={self._chat_id})!")

    async def commit(self) -> None:

        await self._storage.set_magazine_states(chat=self._chat_id, user=self._user_id, states=self._states)
        logger.debug(f"Magazine has committed states {self._states} to storage "
                     f"(user_id={self._user_id}, chat_id={self._chat_id})!")

    async def push(self, state: Optional[str]) -> None:

        if not self.is_loaded:
            await self.load()
        self.set(state)
        await self.commit()

    @property
    def is_loaded(self) -> bool:

        return self._states is not None

    @property
    def states(self) -> List[Optional[str]]:

        if not self.is_loaded:
            raise exceptions.magazine.MagazineIsNotLoadedError("states were not loaded!")

        return self._states

    @property
    def current_state(self) -> Optional[str]:

        return self.states[-1]

    @property
    def penultimate_state(self) -> Optional[str]:

        try:
            return self.states[-2]
        except IndexError:
            raise exceptions.state.StateNotFoundError(f"no penultimate state for (user_id={self._user_id}, "
                                                      f"chat_id={self._chat_id})!")


class BaseStorage(aiogram.dispatcher.storage.BaseStorage, ABC):

    @abstractmethod
    async def set_magazine_states(self, *, chat: Union[str, int, None] = None,
                                  user: Union[str, int, None] = None,
                                  states: List[Optional[str]]) -> None:

        pass

    @abstractmethod
    async def get_magazine_states(self, *, chat: Union[str, int, None] = None,
                                  user: Union[str, int, None] = None) -> List[Optional[str]]:

        pass

    def get_magazine(self, *, chat: Union[str, int, None] = None,
                     user: Union[str, int, None] = None) -> Magazine:

        return Magazine(self, user_id=user, chat_id=chat)
