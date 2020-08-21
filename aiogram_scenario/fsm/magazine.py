from typing import List, Optional
import logging

from aiogram.dispatcher.storage import BaseStorage

from aiogram_scenario import exceptions


logger = logging.getLogger(__name__)


class Magazine:

    def __init__(self, storage: BaseStorage,
                 data_key: str,
                 user_id: Optional[int] = None,
                 chat_id: Optional[int] = None):

        self._storage = storage
        self._data_key = data_key
        self._user_id = user_id
        self._chat_id = chat_id
        self._is_loaded = False
        self._states: Optional[List[str]] = None

    def __str__(self):

        class_part = f"{self.__class__.__name__}"
        if self._is_loaded:
            return f"<{class_part} {self._states}>"
        else:
            return f"<{class_part} NOT LOADED!>"

    __repr__ = __str__

    async def initialize(self, initial_state: str) -> None:

        await self._update_storage([initial_state])
        logger.debug(f"Initialized magazine storage (user_id={self._user_id}, chat_id={self._chat_id})")

    async def load(self) -> None:

        data = await self._storage.get_data(user=self._user_id, chat=self._chat_id)
        try:
            self._states = data[self._data_key]
        except KeyError:
            raise exceptions.MagazineInitializationError("storage has not been initialized!")

        self._is_loaded = True

        logger.debug(f"States loaded into the magazine: {self._states}, "
                     f"(user_id={self._user_id}, chat_id={self._chat_id})")

    @property
    def states(self) -> List[str]:

        if not self._is_loaded:
            raise exceptions.MagazineError("states were not loaded!")

        return self._states

    def set(self, state: str) -> None:

        try:
            state_index = self.states.index(state)
        except ValueError:  # not on the magazine
            self._states.append(state)
        else:  # exists on the magazine
            del self._states[state_index + 1:]

        logger.debug(f"Magazine set state: '{state}' (user_id={self._user_id}, chat_id={self._chat_id})")

    def pop(self) -> str:

        if len(self.states) > 1:
            state = self._states.pop()
        else:
            raise exceptions.MagazineError("you can't pop initial state from magazine!")

        logger.debug(f"State retrieved from magazine: '{state}' (user_id={self._user_id}, chat_id={self._chat_id})")

        return state

    @property
    def current_state(self) -> str:

        return self.states[-1]

    @property
    def penultimate_state(self) -> Optional[str]:

        try:
            return self.states[-2]
        except IndexError:
            return None

    async def commit(self) -> None:

        await self._update_storage(self._states)
        logger.debug(f"Magazine has committed states to storage (user_id={self._user_id}, chat_id={self._chat_id})")

    async def _update_storage(self, states: List[str]) -> None:

        await self._storage.update_data(user=self._user_id, chat=self._chat_id,
                                        data={self._data_key: states})
