import logging
from abc import ABC, abstractmethod

from aiogram_scenario.fsm.transitions.locking.lock_data import LockData
from aiogram_scenario.fsm.transitions.locking.lock_context import LockContext
from aiogram_scenario.fsm.state import BaseState
from aiogram_scenario import exceptions, helpers


logger = logging.getLogger(__name__)


class AbstractLocksStorage(ABC):

    @abstractmethod
    async def check_locking(self, *, chat_id: int, user_id: int) -> bool:

        pass

    @abstractmethod
    async def set_lock(self, *, chat_id: int, user_id: int) -> None:

        pass

    @abstractmethod
    async def unset_lock(self, *, chat_id: int, user_id: int) -> None:

        pass

    def acquire(self, source_state: BaseState, destination_state: BaseState, *,
                chat_id: int, user_id: int) -> LockContext:

        return LockContext(
            storage=self,
            source_state=source_state,
            destination_state=destination_state,
            chat_id=chat_id,
            user_id=user_id
        )

    async def add_lock(self, source_state: BaseState, destination_state: BaseState,
                       chat_id: int, user_id: int) -> LockData:

        chat_id, user_id = helpers.normalize_telegram_ids(chat_id=chat_id, user_id=user_id)
        is_locked = await self.check_locking(chat_id=chat_id, user_id=user_id)
        if is_locked:
            raise exceptions.TransitionLockingError(
                source_state=str(source_state),
                destination_state=str(destination_state),
                chat_id=chat_id,
                user_id=user_id
            )

        await self.set_lock(chat_id=chat_id, user_id=user_id)
        lock_data = LockData(
            source_state=source_state,
            destination_state=destination_state,
            chat_id=chat_id,
            user_id=user_id,
            is_active=True
        )

        logger.debug(f"Lock is set for ({chat_id=}, {user_id=})!")

        return lock_data

    async def remove_lock(self, lock_data: LockData) -> None:

        if not lock_data.is_active:
            raise RuntimeError(f"transition lock ({lock_data}) was removed earlier!")

        await self.unset_lock(chat_id=lock_data.chat_id, user_id=lock_data.user_id)
        lock_data.is_active = False

        logger.debug(f"Lock is unset for (chat_id={lock_data.chat_id}, user_id={lock_data.user_id})!")
