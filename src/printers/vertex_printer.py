

from typing import List

from networkx import DiGraph

from src.printers.abstract_path_printer import AbstractPathPrinter


class VertexPrinter(AbstractPathPrinter):

    def __init__(self, G: DiGraph) -> None:
        self.G = G

    '''
    Prints vertexes along shortest path from source to target
    '''
    def print(self, path: List[str]) -> None:
        print(path)