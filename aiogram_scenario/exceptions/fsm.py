from .base import ScenarioError


class FSMStorageError(ScenarioError):

    pass


class InvalidFSMStorage(FSMStorageError):

    pass


class TransitionAddingError(ScenarioError):

    pass


class TransitionRemovingError(ScenarioError):

    pass


class ExportTransitionsError(ScenarioError):

    pass


class ImportTransitionsError(ScenarioError):

    pass


class TransitionsChronologyError(ScenarioError):

    pass
