from dataclasses import dataclass
from typing import List

from src.graph.edges.abstract_edge import AbstractEdge
from src.graph.edges.effects_edge import EffectsEdge
from src.graph.edges.semantic_edge import SemanticEdge
from src.graph.vertex import Vertex


@dataclass
class Path(object):
    vertexes: List[Vertex]  # vertexes assumed to come in in correct order
    edges: List[AbstractEdge]

    def __post_init__(self) -> None:
        for vertex in self.vertexes:
            is_in_some_edge: bool = False
            for edge in self.edges:
                u = edge.u
                v = edge.v
                if vertex == u or vertex == v:
                    is_in_some_edge = True
            assert is_in_some_edge, "Vertex must be in some edge"

        for edge in self.edges:
            u = edge.u
            v = edge.v
            msg: str = f"{u} from edge {u}-{v} is not in vertexes"
            assert u in self.vertexes, msg
            msg2: str = f"{v} from edge {u}-{v} is not in vertexes"
            assert v in self.vertexes, msg2

    def get_vertex_names(self) -> List[str]:
        output: List[str] = []
        for v in self.vertexes:
            output.append(v.name)
        return output

    def _get_edge(self, u, v):
        return next(e for e in self.edges if e.u == u and e.v == v)

    def get_edge_size_report(self) -> str:
        out: str = ""
        for vertex_number, vertex in enumerate(self.vertexes[0:-1]):
            next_vertex = self.vertexes[vertex_number + 1]
            edge = self._get_edge(vertex, next_vertex)
            if type(edge) == EffectsEdge:
                edge_count = f"({len(edge.data)})"
                out += str(vertex) + "--" + edge_count + "-->"
            else:
                out = out + "-->"

        out = out + str(next_vertex)
        return out


if __name__ == "__main__":

    v1: Vertex = Vertex("a")
    v2: Vertex = Vertex("b")
    v3: Vertex = Vertex("c")
    e1: SemanticEdge = SemanticEdge(u=v1, v=v2, distance=0.3)
    e2: SemanticEdge = SemanticEdge(u=v2, v=v3, distance=0.4)
    Path(vertexes=[v1, v2], edges=[e1])
    Path(vertexes=[v1, v2], edges=[e1, e2])
