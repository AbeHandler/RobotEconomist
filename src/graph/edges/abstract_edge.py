from abc import ABC

from src.graph.vertex import Vertex


class AbstractEdge(ABC):

    def __init__(self, u: Vertex, v: Vertex):
        self.u = u
        self.v = v
        super().__init__()