from src.graph.edges.abstract_edge import AbstractEdge
from src.graph.vertex import Vertex


class EffectsEdge(AbstractEdge):
    def __init__(self, u: Vertex, v: Vertex, data: dict):
        # data is a dictionary w/ metadata about filenames/snippets
        self.data = data
        super().__init__(u, v)


if __name__ == "__main__":
    e = EffectsEdge(
        Vertex("a"), Vertex("b"), {"1": {"filename": "e", "snippet": "s"}}
    )
    print(e)
