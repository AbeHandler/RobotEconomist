from rich.console import Console

from src.graph.edges.abstract_edge import AbstractEdge
from src.graph.edges.effects_edge import EffectsEdge
from src.graph.edges.semantic_edge import SemanticEdge
from src.graph.vertex import Vertex
from src.printers.pre_printer_interface import InformalPreprinterInterface


class EdgePrinter(InformalPreprinterInterface):

    def __init__(self) -> None:
        pass

    def _pre_print_effects_edge(self, edge: EffectsEdge) -> str:
        out: str = ""
        out = out + f"{edge.filename} says that [bold cyan] {edge.u}  [/bold cyan] affects  [bold cyan] {edge.v} [/bold cyan]:\n"  # noqa: E501
        snippet: str = edge.snippet
        return out + f"[italic] {snippet} [\italic]\n"

    def _pre_print_semantic_edge(self, edge: SemanticEdge) -> str:
        return (f"[bold cyan] {edge.u} [/bold cyan] is similar to [bold blue]{edge.v}[/bold blue] (with distance={edge.distance:.2f})\n")  # noqa: E501

    def pre_print(self, **kwargs: dict) -> str:

        edge: AbstractEdge = kwargs['edge']  # type: ignore

        if isinstance(edge, EffectsEdge):
            return self._pre_print_effects_edge(edge)
        elif isinstance(edge, SemanticEdge):
            return self._pre_print_semantic_edge(edge)
        else:
            raise TypeError("Unexpected argument type to pre_print")
            return "For the linter"


if __name__ == "__main__":

    e = SemanticEdge(Vertex("a"), Vertex("b"), .4)
    e2 = EffectsEdge(Vertex("a"), Vertex("b"), filename='e', snippet="s")

    printer_ = EdgePrinter()

    console = Console(record=True)
    console.print(printer_.pre_print(kwargs={"edge": e}))
    console.print(printer_.pre_print(kwargs={"edge": e2}))