

class InitialStateNotSetError(Exception):

    def __init__(self, message=None):

        self.message = message or "initial state not set!"

    def __str__(self):

        return self.message


class StateNotFoundError(Exception):

    pass


class DuplicateError(Exception):

    pass


class TransitionError(Exception):

    pass


class MagazineError(Exception):

    pass


class MagazineInitializationError(MagazineError):

    pass


class MagazineIsNotLoadedError(MagazineError):

    pass
