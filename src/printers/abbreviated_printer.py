from typing import List

from networkx import DiGraph

from src.printers.abstract_path_printer import AbstractPathPrinter


class AbbreviatedPrinter(AbstractPathPrinter):
    """
    Prints the snippets in the causal path from source to target
    """

    def __init__(self, G: DiGraph) -> None:
        self.G = G

    def print(self, path: List[str]) -> None:
        print("->".join([o for o in path]))
