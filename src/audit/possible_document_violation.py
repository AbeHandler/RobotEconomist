from src.audit.abstract_possible_violation import AbstractPossibleViolation
from src.extractors.extraction import Extraction
from src.graph.path import Path


class PossibleDocumentViolation(AbstractPossibleViolation):
    """
    This is a document-based violation in which there is a
    specific instrument and outcome in a doc which are Extractions
    """

    def __init__(self, instrument: Extraction, outcome: Extraction, path: Path):
        self.instrument: Extraction = instrument
        self.outcome: Extraction = outcome
        super().__init__(path=path)
        self._validate_init()
        assert isinstance(self.instrument, Extraction)

    def _validate_init(self) -> None:
        if self.instrument == self.outcome:
            raise ValueError("Instrument can't be the same as outcome")
