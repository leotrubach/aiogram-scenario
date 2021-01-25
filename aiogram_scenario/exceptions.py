from typing import List


class ScenarioError(Exception):

    pass


class TransitionAddingError(ScenarioError):

    pass


class TransitionRemovingError(ScenarioError):

    pass


class InitialStateSettingError(ScenarioError):

    pass


class InitialStateUnsettingError(ScenarioError):

    pass


class InvalidFSMStorageError(ScenarioError):

    def __init__(self, storage_type: str):

        self.storage_type = storage_type

    def __str__(self):

        return (f"invalid storage type '{self.storage_type}'! Try to choose from the ones "
                "suggested here: aiogram_scenario.fsm.storages")


class TransitionError(ScenarioError):

    def __init__(self, source_state: str, destination_state: str,
                 chat_id: int, user_id: int, message: str):

        self.source_state = source_state
        self.destination_state = destination_state
        self.chat_id = chat_id
        self.user_id = user_id
        self.message = message

    def __str__(self):

        return (f"failed transition from '{self.source_state}' to "
                f"'{self.destination_state}'. Cause: {self.message}")


class NextTransitionNotFoundError(TransitionError):

    def __init__(self, source_state: str, chat_id: int, user_id: int):

        super().__init__(
            source_state=source_state,
            destination_state="None",
            chat_id=chat_id,
            user_id=user_id,
            message="next transition not found!"
        )


class TransitionLockingError(TransitionError):

    def __init__(self, source_state: str, destination_state: str,
                 chat_id: int, user_id: int):

        super().__init__(
            source_state=source_state,
            destination_state=destination_state,
            chat_id=chat_id,
            user_id=user_id,
            message="lock is active!"
        )


class MagazineIsNotLoadedError(ScenarioError):

    def __init__(self, chat_id: int, user_id: int):

        self.chat_id = chat_id
        self.user_id = user_id

    def __str__(self):

        return f"states were not loaded (chat_id={self.chat_id}, user_id={self.user_id})!"


class StateNotFoundError(ScenarioError):

    pass


class TransitionsChronologyError(ScenarioError):

    def __init__(self, source_state: str, destination_state: str, states: List[str]):

        self.source_state = source_state
        self.destination_state = destination_state
        self.states = states

    def __str__(self):

        return (f"it is impossible to get from state '{self.source_state}' "
                f"to state '{self.destination_state}'!")


class TransitionsImportError(ScenarioError):

    pass


class HandlerRegistrationError(ScenarioError):

    pass


class CodeGenerationError(ScenarioError):

    pass


class StateNotAddedToFSMError(ScenarioError):

    pass
