from abc import ABC, abstractmethod
from typing import Dict


class AbstractTransitionsStorage(ABC):

    def __init__(self, filename: str):

        self._filename = filename

    @abstractmethod
    def read(self) -> Dict[str, Dict[str, str]]:

        pass

    @abstractmethod
    def write(self, transitions: Dict[str, Dict[str, str]]) -> None:

        pass
