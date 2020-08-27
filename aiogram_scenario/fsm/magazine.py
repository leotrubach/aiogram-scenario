from typing import List, Optional
import logging

from aiogram_scenario.fsm.storages import BaseStorage
from aiogram_scenario import exceptions


logger = logging.getLogger(__name__)


class Magazine:

    def __init__(self, storage: BaseStorage, *,
                 user_id: Optional[int] = None,
                 chat_id: Optional[int] = None):

        if chat_id is None and user_id is None:
            raise ValueError(f"at least one parameter must be specified ({user_id=}, {chat_id=})!")

        self._storage = storage
        self._user_id = user_id
        self._chat_id = chat_id
        self._states: List[str] = []

    def __str__(self):

        class_part = f"{self.__class__.__name__}"
        try:
            return f"<{class_part} {self.states}>"
        except exceptions.MagazineIsNotLoadedError:
            return f"<{class_part} NOT LOADED!>"

    __repr__ = __str__

    @property
    def is_loaded(self) -> bool:

        return bool(self._states)

    async def initialize(self, initial_state: str) -> None:

        states = [initial_state]
        await self._update_storage(states)
        self._states = states

        logger.debug(f"Initialized magazine storage (user_id={self._user_id}, chat_id={self._chat_id})")

    async def load(self) -> None:

        states = await self._storage.get_magazine(chat=self._chat_id, user=self._user_id)
        if not states:
            raise exceptions.MagazineInitializationError("storage has not been initialized!")
        self._states = states

        logger.debug(f"States loaded into the magazine: {self._states}, "
                     f"(user_id={self._user_id}, chat_id={self._chat_id})")

    @property
    def states(self) -> List[str]:

        if not self.is_loaded:
            raise exceptions.MagazineIsNotLoadedError("states were not loaded!")

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
        logger.debug(f"Magazine has committed states {self._states} to storage "
                     f"(user_id={self._user_id}, chat_id={self._chat_id})")

    async def _update_storage(self, states: List[str]) -> None:

        await self._storage.set_magazine(chat=self._chat_id, user=self._user_id, states=states)
