from abc import ABC
from enum import Enum

from src.graph.edges.abstract_edge import AbstractEdge
from src.graph.edges.effects_edge import EffectsEdge
from src.graph.edges.semantic_edge import SemanticEdge
from src.graph.path import Path


class EdgeTypes(Enum):
    effects: EffectsEdge = EffectsEdge
    semantics: SemanticEdge = SemanticEdge


class AbstractPossibleViolation(ABC):
    """
    There are at least two kinds of possible violations.
    1. First, the there is a document-based violation in which there is a
      specific instrument and outcome in a doc which are Extractions
    2. Then there is a hypothetical violation in which there is no doc but
      if you were to have this instrument and outcome there would be a
      violation

    All that is required for the abstract violation is a path

    Each of these has its own subclass
    """

    def __init__(self, path: Path):
        self.path: Path = path

    def is_only_semantic(self) -> bool:
        """
        Returns true if all edges in path are of type SemanticEdge, else False
        """
        return all(self._is_semantic(i) for i in self.path.edges)

    def total_semantic(self) -> bool:
        """
        Returns count of semantic edges
        """
        return sum(1 for i in self.path.edges if self._is_semantic(i))

    def max_semantic_distance(self) -> float:
        """
        You may want to exclude cases where violations are less than
        some threshold
        """
        max_: float = 0.0
        for edge in self.path.edges:
            if isinstance(edge, EdgeTypes.semantics.value):
                # we know this is a semantic edge now
                if edge.distance > max_:  # type: ignore
                    max_ = float(edge.distance)  # type: ignore
        return max_

    def _validate_semantic_check(self, edge: AbstractEdge) -> None:
        ok = False
        for edge_type in EdgeTypes:
            if isinstance(edge, edge_type.value):
                ok = True
        if not ok:
            raise ValueError(f"type{edge} not in EdgeTypes")

    def _is_semantic(self, edge: AbstractEdge) -> bool:
        self._validate_semantic_check(edge)

        if isinstance(edge, EdgeTypes.semantics.value):  # noqa
            return True
        else:
            return False
