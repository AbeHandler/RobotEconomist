from enum import Enum

from src.audit.abstract_possible_violation import AbstractPossibleViolation
from src.graph.edges.effects_edge import EffectsEdge
from src.graph.edges.semantic_edge import SemanticEdge
from src.graph.path import Path


class EdgeTypes(Enum):
    effects = EffectsEdge
    semantics = SemanticEdge


class HypotheticalViolation(AbstractPossibleViolation):
    """
    A hypothetical violation in which there is no doc w/ bad instrument and
    bad outcome but if you were to have this instrument and outcome
    there would be a violation. In this case, instrument and outcome are
    strings which should be at start and end of path
    """

    def __init__(self, path: Path, instrument: str, outcome: str):
        self.path: Path = path
        self.instrument = instrument
        self.outcome = outcome
        self._validate()

    def _validate(self) -> None:
        """
        Path should be from instrument to outcome
        """
        start = self.path.edges[0].u.name
        end = self.path.edges[-1].v.name
        if not start == self.instrument:
            raise ValueError("Instrument must come at start of path")
        if not end == self.outcome:
            raise ValueError("Outcome must come at end of path")
