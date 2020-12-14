from .base import ScenarioError


class StateError(ScenarioError):

    pass


class InitialStateError(StateError):

    pass


class StateNotFoundError(StateError):

    pass
