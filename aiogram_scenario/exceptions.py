

class StateError(Exception):

    pass


class InitialStateError(StateError):

    pass


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
