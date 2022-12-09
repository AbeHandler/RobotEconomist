import json
from typing import Generator, List

from networkx import (  # fmt: off # onflict b/ween black and isort #noqa: E501
    DiGraph,
    all_simple_paths,
    bfs_tree,
    node_link_graph,
    shortest_path,
)

from src.audit.hypothetical_violation import HypotheticalViolation
from src.audit.possible_document_violation import PossibleDocumentViolation
from src.audit.violation_factory import ViolationFactory
from src.extractors.extraction import Extraction


class Auditor(object):
    """
    More or less a wrapper over networkx.

    It reasons over graph specifications to find IV violations

    It returns violations as Paths, which is my abstraction over graphs

    Paths are easier to reason about and print than networkx.path which is a
    list of string. I guess my Path object could somehow extend the networkx
    path but not sure it is worth it or important to do that.
    """

    def __init__(
        self,
        graph_specification: str,
    ) -> None:
        self.graph = self._load_graph(graph_specification)
        self.violation_factory = ViolationFactory(self.graph)

    def get_possible_violation(
        self, instrument: Extraction, outcome: Extraction
    ) -> PossibleDocumentViolation:
        path: List[str] = shortest_path(
            self.graph,
            source=instrument.text_of_extraction,
            target=outcome.text_of_extraction,
        )
        return self.violation_factory.get_document_violation(
            source=instrument, target=outcome, list_of_networkx_vertexes=path
        )

    def has_iv_violation(
        self,
        proposed_instrument: str,
        proposed_outcome: str,
        depth_limit: int = 5,
    ) -> bool:

        self._check_valid_query(
            proposed_variable=proposed_instrument, variable_kind="instrument"
        )
        self._check_valid_query(
            proposed_variable=proposed_outcome, variable_kind="outcome"
        )

        can_reach: List[str] = self._explore_down_from_vertex(
            vertex=proposed_instrument, depth_limit=depth_limit
        )

        return proposed_outcome in can_reach

    def _load_graph(self, graph_specification: str) -> DiGraph:
        with open(graph_specification, "r") as inf:
            graph: dict = json.load(inf)
        return node_link_graph(graph)

    def _explore_down_from_vertex(
        self, vertex: str, depth_limit: int = 5
    ) -> List[str]:
        """
        Search down the tree from a given vertex using dfs
        """
        nodes: List[str] = list(
            bfs_tree(self.graph, vertex, depth_limit=depth_limit).nodes()
        )
        return nodes

    def _get_nx_paths_to_target(
        self, target: str
    ) -> Generator[List[str], None, None]:
        # note that the bfs is reversed! So you are going against the
        # direction of x affects y.
        tree: DiGraph = bfs_tree(self.graph, target, reverse=True)

        # the ancestors are possible b/c we are ignoring direction
        possible_ancestors: List[str] = list(tree.nodes())

        for possible_ancestor in possible_ancestors:
            path: List[str] = shortest_path(
                self.graph, source=possible_ancestor, target=target
            )
            if len(path) > 1:
                yield path

    def get_all_hypothetical_violations_from_instrument_to_outcome(
        self, instrument: str, outcome: str, cutoff: int = 5
    ) -> List[HypotheticalViolation]:
        network_x_paths = self._get_all_networkx_paths(
            source=instrument, target=outcome, cutoff=cutoff
        )
        return self._nx_paths_to_possible_violations(network_x_paths)

    def get_all_hypothetical_violations_to_outcome(
        self, target: str
    ) -> List[HypotheticalViolation]:
        network_x_paths = self._get_nx_paths_to_target(target)
        return self._nx_paths_to_possible_violations(network_x_paths)

    def _nx_paths_to_possible_violations(
        self, network_x_paths: Generator[List[str], None, None]
    ) -> List[HypotheticalViolation]:
        out: List[HypotheticalViolation] = []
        for path in network_x_paths:
            instrument = path[0]
            outcome = path[-1]
            out.append(
                self.violation_factory.get_hypothetical_violation(
                    instrument=instrument,
                    outcome=outcome,
                    list_of_networkx_vertexes=path,
                )
            )
        return out

    def _get_all_networkx_paths(
        self, source: str, target: str, cutoff: int = 3
    ) -> Generator[List[str], None, None]:
        for path in all_simple_paths(
            self.graph, source=source, target=target, cutoff=cutoff
        ):
            yield path

    def get_hypothetical_violation(
        self, path: List[str], instrument: str, outcome: str
    ) -> HypotheticalViolation:

        return self.violation_factory.get_hypothetical_violation(
            instrument=instrument,
            outcome=outcome,
            list_of_networkx_vertexes=path,
        )

    def _check_valid_query(
        self, proposed_variable: str, variable_kind: str
    ) -> bool:
        if proposed_variable in set(self.graph.nodes):
            return True
        else:
            # e.g., "cant look for instrument asjelira4a because ... "
            msg = f"The auditor can't look for violations for the {variable_kind} {proposed_variable} because it is not a known variable."  # noqa: E501
            msg = msg + " Try another instrument "
            msg = msg + "(hint: do you need to use semantic similarity?)"
            raise AttributeError(msg)
