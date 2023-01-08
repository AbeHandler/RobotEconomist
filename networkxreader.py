# %%
import json
from dataclasses import dataclass
from typing import List, Set

from networkx import (  # fmt: off # onflict b/ween black and isort #noqa: E501
    DiGraph,
    ancestors,
    node_link_graph,
)


@dataclass
class DataClassOVB:
    ancestors: List[str]
    X: str
    Y: str


def load_graph(graph_specification: str) -> DiGraph:
    """
    Load a graph from a json file
    e.g. data/nber_abstracts/graphs/rulebased.extractions.jsonl.nxdigraph.json
    """
    with open(graph_specification, "r") as inf:
        graph: dict = json.load(inf)
        return node_link_graph(graph)


def has_common_ancestors_networkx(graph: DiGraph, node1: str, node2: str):
    node1_ancestors = set(ancestors(graph, node1))
    node2_ancestors = set(ancestors(graph, node2))
    common_ancestors = node1_ancestors.intersection(node2_ancestors)
    return len(common_ancestors) > 0


def find_common_ancestors_networkx(
    graph: DiGraph, node1: str, node2: str
) -> Set[str]:
    """
    Find the common ancestors of two nodes in a graph
    """
    node1_ancestors = set(ancestors(graph, node1))
    node2_ancestors = set(ancestors(graph, node2))
    common_ancestors = node1_ancestors.intersection(node2_ancestors)
    if not has_common_ancestors_networkx(graph, node1, node2):
        raise ValueError("No common ancestors")
    return common_ancestors


def create_simple_digraph_networkx():
    """
    Create a simple directed graph in networkx
    """
    import networkx as nx

    G = nx.DiGraph()
    G.add_edge("A", "B")
    G.add_edge("B", "C")
    G.add_edge("B", "D")
    G.add_edge("C", "E")
    G.add_edge("D", "E")
    return G


def print_graph_networkx(G: DiGraph):
    """
    Print a graph in networkx
    """
    import networkx as nx

    nx.draw(G, with_labels=True)
    import matplotlib.pyplot as plt

    plt.show()


def find_potential_OVB(G: DiGraph):
    """
    Find all potential OVB
    """
    output: List[DataClassOVB] = []
    for edge in list(G.edges(data=True)):
        u, v, data = edge
        if has_common_ancestors_networkx(G, u, v):
            common_ancestors = find_common_ancestors_networkx(G, u, v)
            output.append(DataClassOVB(common_ancestors, X=u, Y=v))
    return output


def get_path_between_nodes_networkx(G: DiGraph, node1: str, node2: str):
    """
    Get the path between two nodes in a graph
    """
    import networkx as nx

    return nx.shortest_path(G, node1, node2)


tot = find_potential_OVB(
    load_graph(
        "data/nber_abstracts/graphs/rulebased.extractions.jsonl.nxdigraph.json"
    )
)

print(len(tot))

# %%

simple_graph = create_simple_digraph_networkx()
common_ancestors = find_common_ancestors_networkx(simple_graph, "E", "D")
