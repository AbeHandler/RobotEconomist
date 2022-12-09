from enum import Enum
from re import I
from typing import List, Tuple

from networkx import DiGraph

from src.audit.hypothetical_violation import HypotheticalViolation
from src.audit.possible_document_violation import PossibleDocumentViolation
from src.extractors.extraction import Extraction
from src.graph.edges.abstract_edge import AbstractEdge
from src.graph.edges.effects_edge import EffectsEdge
from src.graph.edges.semantic_edge import SemanticEdge
from src.graph.path import Path
from src.graph.vertex import Vertex


class EdgeData(Enum):
    distance: str = "distance"
    snippet: str = "snippet"
    filename: str = "filename"


class ViolationFactory(object):
    """
    The auditor finds violations in networkx graphs.

    But we need to print/reason over possible violations
    e.g. by determining if all of the edges are semantic
    or by filtering out by distance. All of the information
    about the violation is held in a PossibleViolation object

    So this class basically converts networkx paths from the
    auditor into possible violations

    The input of get_violation is a networkx path which is a list of string
    The output is
    """

    def __init__(self, G: DiGraph) -> None:
        self.G = G

    def _validate_violation(
        self, source: str, target: str, path: List[str]
    ) -> None:
        if source != path[0]:
            raise ValueError("Source must be start of path")
        if target != path[-1]:
            raise ValueError("Target must be end of path")
        if len(path) < 2:
            msg = f"{source}, {target}, {path}"
            raise ValueError("Minimum length for a path is 2: " + msg)

    def _make_edge(self, u: Vertex, v: Vertex, data: dict) -> AbstractEdge:

        if EdgeData.distance.name in data:
            return SemanticEdge(
                u=u,
                v=v,
                distance=data[EdgeData.distance.name],
            )
        else:
            return EffectsEdge(u=u, v=v, data=data)

    def get_hypothetical_violation(
        self,
        instrument: str,
        outcome: str,
        list_of_networkx_vertexes: List[str],
    ) -> HypotheticalViolation:
        path: Path = self._network_x_path_to_path_object(
            list_of_networkx_vertexes
        )
        return HypotheticalViolation(
            path=path, instrument=instrument, outcome=outcome
        )

    def get_document_violation(
        self,
        source: Extraction,
        target: Extraction,
        list_of_networkx_vertexes: List[str],
    ) -> PossibleDocumentViolation:
        self._validate_violation(
            source.text_of_extraction,
            target.text_of_extraction,
            list_of_networkx_vertexes,
        )

        path: Path = self._network_x_path_to_path_object(
            list_of_networkx_vertexes
        )

        return PossibleDocumentViolation(
            instrument=source,
            outcome=target,
            path=path,
        )

    def _list2edges(
        self, list_of_network_vertexes: List[str]
    ) -> List[Tuple[str, str]]:
        """
        Take a list of networkx vertex names and turn them into a list
        f (u, v) pairs. Essentially take the 2-grams from the list
        """
        edges: List[Tuple[str, str]] = []
        for ino, i in enumerate(list_of_network_vertexes):
            if ino < (len(list_of_network_vertexes) - 1):
                edges.append(
                    (
                        list_of_network_vertexes[ino],
                        list_of_network_vertexes[ino + 1],
                    )
                )
        return edges

    def _network_x_path_to_path_object(
        self, list_of_network_vertexes: List[str]
    ) -> Path:
        """
        NetworkX shortest path algos return paths which are
        lists of vertex names. But we need information
        about those paths so have our own Path object
        to store the info. This function takes a
        networkx path and makes a Path object.
        """
        vertexes: List[Vertex] = []
        edges = []

        # first make the vertexes
        vertexes = [Vertex(v) for v in list_of_network_vertexes]
        string2vertex = {v.name: v for v in vertexes}

        for edge in self._list2edges(list_of_network_vertexes):
            u, v = edge
            data = self.G.edges[edge]
            edges.append(
                self._make_edge(string2vertex[u], string2vertex[v], data)
            )

        return Path(vertexes, edges)
