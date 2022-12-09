from multiprocessing.sharedctypes import Value
from typing import List

from networkx import DiGraph
from rich.console import Console

from src.corpus import Corpus
from src.graph.path import Path
from src.printers.abstract_path_printer import AbstractPathPrinter


class SnippetsPrinter(AbstractPathPrinter):
    """
    Prints the snippets in the causal path from source to target
    """

    def __init__(self, G: DiGraph, corpus: Corpus) -> None:
        self.G = G
        self.corpus = corpus

    def get_abbreviated_report(self, path: List[str]) -> str:
        return "->".join([o for o in path])

    def pre_print(self, path: List[str]) -> str:

        causal_chain = (
            f"[bold red]{path[0]}[/bold red]"
            + " affects "
            + f"[bold red]{path[-1]}[/bold red]"
        )
        out: str = ""
        out = out + f"There is evidence that {causal_chain} \n\n"

        out = out + f"[bold red]{path[0]}[/bold red] "
        out = out + f"[bold red]{'->'.join(path[1:-1])}[/bold red]"
        out = out + f" [bold red]{path[-1]}[/bold red]\n"

        all_but_last_vertex: List[str] = path[0:-1]

        for path_step, vertex in enumerate(all_but_last_vertex):
            out = out + ""
            u: str = vertex
            v: str = path[path_step + 1]
            if not self.G.has_edge(u, v):
                msg: str = (
                    f"There is no edge '{u}'-'{v}' in graph but it is in "
                )
                msg = msg + "your path. Did you reorder vertexes?"
                raise ValueError(msg)
            data = self.G.get_edge_data(u, v)

            if "distance" in data:
                out = (
                    out
                    + f"[bold]{u}[/bold] is similar to [bold]{v}[/bold] (with distance={data['distance']:.2f})\n"
                )  # noqa: E501
            else:

                # each time an edge pais appears a new key is added to data
                # so if A->B appears 4 times then data will have keys 1 to 4
                # each key is associated w/ a value explaining the A->B
                # relationship in a ceratin paper
                for k in data.keys():

                    one_item_in_data = data[k]
                    s2id = (
                        one_item_in_data["filename"]
                        .split("_")[0]
                        .split("/")
                        .pop()
                    )
                    metadata = self.corpus.get(s2id)

                    title = metadata["title"]
                    journal = metadata["journal"]

                    s2url: str = (
                        f"https://api.semanticscholar.org/CorpusID:{s2id}"
                    )

                    out = (
                        out
                        + f"\n\n The paper '{title}' from the publication '{journal}' reports that [bold red]{u}[/bold red] affects [bold red]{v}[/bold red]:\n"
                    )
                    snippet: str = one_item_in_data["snippet"].replace(
                        u, f"[bold red]{u}[/bold red]"
                    )
                    snippet = snippet.replace(v, f"[bold red]{v}[/bold red]")
                    out = out + f"[italic] {snippet} [\italic]\n"
                    out = out + f"For more detail see {s2url}\n"
                    out = out + "\n"
        return out

    def print(self, list_of_vertexes: List[str]) -> None:

        if len(list_of_vertexes) < 2:
            raise ValueError("Path must have a length greater than 1")

        console = Console()

        print("")
        print("[*] start of report")

        out: str = self.pre_print(list_of_vertexes)

        console.print(out)

        print("")
        print("[*] end of report")
