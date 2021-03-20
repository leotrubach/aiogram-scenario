from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from aiogram_scenario.fsm.state import BaseState


class BaseError(Exception):

    def __str__(self):

        return self.message

    @property
    def message(self) -> str:

        return "an error has occurred!"


class InvalidFSMStorageTypeError(BaseError):

    def __init__(self, storage_type: type):

        self.storage_type = storage_type

    @property
    def message(self) -> str:

        return f"""invalid storage type '{self.storage_type.__name__}'!
Choose storage at aiogram_scenario.fsm.storages!"""


class TransitionError(BaseError):

    def __init__(self, chat_id: int, user_id: int,
                 source_state: str, destination_state: str):

        self.chat_id = chat_id
        self.user_id = user_id
        self.source_state = source_state
        self.destination_state = destination_state

    @property
    def message(self) -> str:

        return (f"failed to execute the transition from '{self.source_state}' to '{self.destination_state}' "
                f"(chat_id={self.chat_id}, user_id={self.user_id})!")


class TransitionLockIsActiveError(BaseError):

    def __init__(self, chat_id: int, user_id: int):

        self.chat_id = chat_id
        self.user_id = user_id

    @property
    def message(self) -> str:

        return f"lock is active (chat_id={self.chat_id}, user_id={self.user_id})!"


class TransitionIsLockedError(BaseError):

    def __init__(self, chat_id: int, user_id: int, source_state: BaseState, destination_state: BaseState):

        self.chat_id = chat_id
        self.user_id = user_id
        self.source_state = source_state
        self.destination_state = destination_state

    @property
    def message(self) -> str:

        return (f"failed to execute the transition from '{self.source_state}' to '{self.destination_state}' "
                f"(chat_id={self.chat_id}, user_id={self.user_id}) because there is an active lock!'")


class TransitionAddingError(BaseError):

    def __init__(self, source_state: BaseState, destination_state: BaseState,
                 handler: str, direction: Optional[str]):

        self.source_state = source_state
        self.destination_state = destination_state
        self.handler = handler
        self.direction = direction

    @property
    def message(self) -> str:

        return (f"failed to add transition (source_state='{self.source_state}', "
                f"destination_state='{self.destination_state}', handler={self.handler!r}, "
                f"direction={self.direction!r})!")


class TransitionIsExistsError(BaseError):

    def __init__(self, source_state: BaseState, existing_destination_state: BaseState,
                 handler: str, direction: Optional[str]):

        self.source_state = source_state
        self.exists_destination_state = existing_destination_state
        self.handler = handler
        self.direction = direction

    @property
    def message(self) -> str:

        return (f"transition (source_state='{self.source_state}', handler={self.handler!r}, "
                f"direction={self.direction!r}) already exists "
                f"(existing_destination_state='{self.exists_destination_state}')!")


class TransitionRemovingError(BaseError):

    def __init__(self, source_state: BaseState, handler: str, direction: Optional[str]):

        self.source_state = source_state
        self.handler = handler
        self.direction = direction

    @property
    def message(self) -> str:

        return (f"failed to remove transition (source_state='{self.source_state}', handler={self.handler!r},"
                f"direction={self.direction!r})!")


class TransitionNotFoundError(BaseError):

    def __init__(self, source_state: BaseState, handler: str, direction: Optional[str]):

        self.source_state = source_state
        self.handler = handler
        self.direction = direction

    @property
    def message(self) -> str:

        return (f"transition (source_state='{self.source_state}', handler={self.handler!r}, "
                f"direction={self.direction!r}) not found!")


class NextTransitionNotFoundError(BaseError):

    def __init__(self, chat_id: int, user_id: int):

        self.chat_id = chat_id
        self.user_id = user_id

    @property
    def message(self) -> str:

        return f"next transition not found (chat_id={self.chat_id}, user_id={self.user_id})!"


class BackTransitionNotFoundError(BaseError):

    def __init__(self, chat_id: int, user_id: int):

        self.chat_id = chat_id
        self.user_id = user_id

    @property
    def message(self) -> str:

        return f"back transition not found (chat_id={self.chat_id}, user_id={self.user_id})!"


class StateNotFoundError(BaseError):

    def __init__(self, state: BaseState):

        self.state = state

    @property
    def message(self) -> str:

        return f"state '{self.state}' not found!"


class StateValueNotFoundError(BaseError):

    def __init__(self, value):

        self.value = value

    @property
    def message(self) -> str:

        return f"state value {self.value!r} not found!"


class StateNotFoundInMagazineError(BaseError):

    def __init__(self, chat_id: int, user_id: int, state):

        self.chat_id = chat_id
        self.user_id = user_id
        self.state = state

    @property
    def message(self) -> str:

        return f"state '{self.state}' not found in magazine (chat_id={self.chat_id}, user_id={self.user_id})!"


class PenultimateStateNotFoundInMagazineError(BaseError):

    def __init__(self, chat_id: int, user_id: int, states):

        self.chat_id = chat_id
        self.user_id = user_id
        self.states = states

    @property
    def message(self) -> str:

        return (f"penultimate state not found in magazine (chat_id={self.chat_id}, "
                f"user_id={self.user_id}, states={self.states})!")


class InitialStateIsAlreadySetError(BaseError):

    @property
    def message(self) -> str:

        return "initial state has already been set earlier!"


class FSMIsNotInitializedError(BaseError):

    @property
    def message(self) -> str:

        return "FSM has not been initialized!"


class MagazineIsNotLoadedError(BaseError):

    def __init__(self, chat_id: int, user_id: int):

        self.chat_id = chat_id
        self.user_id = user_id

    @property
    def message(self):

        return "magazine is not loaded!"
