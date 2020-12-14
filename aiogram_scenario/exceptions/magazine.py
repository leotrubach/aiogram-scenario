from .base import ScenarioError


class MagazineError(ScenarioError):

    pass


class MagazineIsNotLoadedError(MagazineError):

    pass
