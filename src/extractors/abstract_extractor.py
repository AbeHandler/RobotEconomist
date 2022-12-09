from abc import ABC, abstractmethod
from typing import List

from spacy.tokens import Doc

from src.extractors.extraction import Extraction


class AbstractExtractor(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_instruments(self, doc: Doc) -> List[Extraction]:
        pass

    @abstractmethod
    def get_outcomes(self, doc: Doc) -> List[Extraction]:
        pass
