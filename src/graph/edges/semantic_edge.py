from src.graph.edges.abstract_edge import AbstractEdge
from src.graph.vertex import Vertex


class SemanticEdge(AbstractEdge):

    def __init__(self, u: Vertex, v: Vertex, distance: float):
        self.distance = distance
        super().__init__(u, v)


if __name__ == "__main__":
    e = SemanticEdge(Vertex("a"), Vertex("b"), .4)
    print(e)
