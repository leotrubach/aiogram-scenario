import logging
from abc import ABC, abstractmethod

from aiogram_scenario.fsm.transitions.locking.lock_context import LockContext
from aiogram_scenario import errors


logger = logging.getLogger(__name__)


class AbstractLockingStorage(ABC):

    @abstractmethod
    async def set(self, *, chat_id: int, user_id: int) -> None:

        pass

    @abstractmethod
    async def unset(self, *, chat_id: int, user_id: int) -> None:

        pass

    @abstractmethod
    async def check(self, *, chat_id: int, user_id: int) -> bool:

        pass

    def acquire(self, *, chat_id: int, user_id: int) -> LockContext:

        return LockContext(storage=self, chat_id=chat_id, user_id=user_id)

    async def add(self, chat_id: int, user_id: int) -> None:

        is_locked = await self.check(chat_id=chat_id, user_id=user_id)
        if is_locked:
            raise errors.TransitionLockIsActiveError(chat_id=chat_id, user_id=user_id)

        await self.set(chat_id=chat_id, user_id=user_id)

        logger.debug(f"Lock is set for ({chat_id=}, {user_id=})!")

    async def remove(self, *, chat_id: int, user_id: int) -> None:

        await self.unset(chat_id=chat_id, user_id=user_id)

        logger.debug(f"Lock is unset ({chat_id=}, {user_id=})!")
