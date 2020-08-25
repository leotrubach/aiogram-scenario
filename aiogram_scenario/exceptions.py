from typing import Optional

from aiogram_scenario.fsm.state import AbstractState


class StateError(Exception):

    pass


class StateNotFoundError(StateError):

    pass


class StateNotAssignedError(StateError):

    pass


class AddingStateError(StateError):

    pass


class InitialStateError(StateError):

    pass


class SettingInitialStateError(InitialStateError):

    pass


class DuplicateError(Exception):

    pass


class TransitionError(Exception):

    pass


class TransitionLockingError(TransitionError):

    def __init__(self, source_state: AbstractState,
                 destination_state: AbstractState,
                 user_id: Optional[int] = None,
                 chat_id: Optional[int] = None):

        self.source_state = source_state
        self.destination_state = destination_state
        self.user_id = user_id
        self.chat_id = chat_id

    def __str__(self):

        return f"transition from '{self.source_state}' to '{self.destination_state}' " \
               f"for (user_id={self.user_id}, chat_id={self.chat_id}) is not possible " \
               f"because there is an active lock!"


class MagazineError(Exception):

    pass


class MagazineInitializationError(MagazineError):

    pass


class MagazineIsNotLoadedError(MagazineError):

    pass
