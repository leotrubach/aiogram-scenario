from typing import Optional, Tuple
from dataclasses import dataclass
import logging

from aiogram_scenario.fsm.state import AbstractState
from aiogram_scenario import exceptions


logger = logging.getLogger(__name__)


@dataclass()
class TransitionLock:

    source_state: AbstractState
    destination_state: AbstractState
    user_id: Optional[int]
    chat_id: Optional[int]
    is_active: bool


class TransitionLockContext:

    def __init__(self, storage: "TransitionsLocksStorage",
                 source_state: AbstractState,
                 destination_state: AbstractState,
                 user_id: Optional[int],
                 chat_id: Optional[int]):

        self._storage = storage
        self._source_state = source_state
        self._destination_state = destination_state
        self._user_id = user_id
        self._chat_id = chat_id
        self._lock: Optional[TransitionLock] = None

    def __enter__(self):

        self._lock = self._storage.add(
            source_state=self._source_state,
            destination_state=self._destination_state,
            user_id=self._user_id,
            chat_id=self._chat_id
        )

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa

        self._storage.remove(self._lock)


class TransitionsLocksStorage:

    def __init__(self):

        self._locks = {}

    def acquire(self, source_state: AbstractState,
                destination_state: AbstractState, *,
                user_id: Optional[int] = None,
                chat_id: Optional[int] = None) -> TransitionLockContext:

        return TransitionLockContext(
            storage=self,
            source_state=source_state,
            destination_state=destination_state,
            user_id=user_id,
            chat_id=chat_id
        )

    def add(self, source_state: AbstractState,
            destination_state: AbstractState, *,
            user_id: Optional[int] = None,
            chat_id: Optional[int] = None) -> TransitionLock:

        is_locked = self._check_locking(user_id=user_id, chat_id=chat_id)
        if is_locked:
            raise exceptions.transition.TransitionLockingError(
                source_state=source_state,
                destination_state=destination_state,
                user_id=user_id,
                chat_id=chat_id
            )

        self._set_lock(user_id=user_id, chat_id=chat_id)
        lock = TransitionLock(
            source_state=source_state,
            destination_state=destination_state,
            user_id=user_id,
            chat_id=chat_id,
            is_active=True
        )

        logger.debug(f"Lock is set for ({user_id=}, {chat_id=})!")

        return lock

    def remove(self, lock: TransitionLock) -> None:

        if not lock.is_active:
            raise RuntimeError(f"transition lock ({lock}) was removed earlier!")

        self._unset_lock(user_id=lock.user_id, chat_id=lock.chat_id)
        lock.is_active = False

        logger.debug(f"Lock is unset for (user_id={lock.user_id}, chat_id={lock.chat_id})!")

    @staticmethod
    def _resolve_address(*, user_id: Optional[int], chat_id: Optional[int]) -> Tuple[int, int]:

        if chat_id is None and user_id is None:
            raise ValueError("'user' or 'chat' parameter is required but no one is provided!")

        if user_id is None and chat_id is not None:
            user_id = chat_id
        elif user_id is not None and chat_id is None:
            chat_id = user_id

        return user_id, chat_id

    def _set_lock(self, *, user_id: Optional[int], chat_id: Optional[int]) -> None:

        user_id, chat_id = self._resolve_address(user_id=user_id, chat_id=chat_id)

        try:
            self._locks[chat_id].add_transition(user_id)
        except KeyError:
            self._locks[chat_id] = {user_id}

    def _unset_lock(self, *, user_id: Optional[int], chat_id: Optional[int]) -> None:

        user_id, chat_id = self._resolve_address(user_id=user_id, chat_id=chat_id)

        chat_users_ids: set = self._locks[chat_id]
        chat_users_ids.remove(user_id)
        if not chat_users_ids:
            del self._locks[chat_id]

    def _check_locking(self, *, user_id: Optional[int] = None, chat_id: Optional[int] = None) -> bool:

        user_id, chat_id = self._resolve_address(user_id=user_id, chat_id=chat_id)

        try:
            chat_users_ids: set = self._locks[chat_id]
        except KeyError:
            return False
        else:
            return user_id in chat_users_ids
