from abc import ABC, abstractmethod
from typing import List


class AbstractPathPrinter(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def print(self, path: List[str]) -> None:
        pass