from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
import logging

from aiogram_scenario import errors
if TYPE_CHECKING:
    from .storage import BaseStorage


logger = logging.getLogger(__name__)


class Magazine:

    __slots__ = ("user_id", "chat_id", "_storage", "_states")

    def __init__(self, storage: BaseStorage, *, chat_id: int, user_id: int):

        self.chat_id = chat_id
        self.user_id = user_id
        self._storage = storage
        self._states: Optional[list] = None

    def __str__(self):

        class_name = type(self).__name__
        try:
            return f"<{class_name} {self.states}>"
        except errors.MagazineIsNotLoadedError:
            return f"<{class_name} NOT LOADED!>"

    __repr__ = __str__

    async def load(self) -> None:

        self._states = await self._storage.get_magazine_states(chat=self.chat_id, user=self.user_id)

        logger.debug(f"States loaded into the magazine: {self._states}, "
                     f"(chat_id={self.chat_id}, user_id={self.user_id})!")

    def set(self, state) -> None:

        try:
            state_index = self.states.index(state)
        except ValueError:  # not on the magazine
            self._states.append(state)
        else:  # exists on the magazine
            del self._states[state_index + 1:]

        logger.debug(f"Magazine set state: {state!r} (chat_id={self.chat_id}, user_id={self.user_id})!")

    async def commit(self) -> None:

        await self._storage.set_magazine_states(chat=self.chat_id, user=self.user_id, states=self._states)
        logger.debug(f"Magazine has committed states {self._states} to storage "
                     f"(chat_id={self.chat_id}, user_id={self.user_id})!")

    async def push(self, state) -> None:

        self.set(state)
        await self.commit()

    async def reset(self) -> None:

        await self._storage.set_state(chat=self.chat_id, user=self.user_id)  # default state is None

    @property
    def is_loaded(self) -> bool:

        return self._states is not None

    @property
    def states(self) -> List[Optional[str]]:

        self._check_loading()
        return self._states

    @property
    def current_state(self) -> Optional[str]:

        return self.states[-1]

    @property
    def penultimate_state(self) -> Optional[str]:

        try:
            return self.states[-2]
        except IndexError:
            raise errors.PenultimateStateNotFoundInMagazineError(chat_id=self.chat_id, user_id=self.user_id,
                                                                 states=self.states)

    def _check_loading(self):

        if not self.is_loaded:
            raise errors.MagazineIsNotLoadedError(chat_id=self.chat_id, user_id=self.user_id)
