import json
from collections import defaultdict
from typing import List, Tuple

from tqdm import tqdm as tqdm

from src.graph_builders.edge_builders.abstract_edge_builder import AbstractEdgeBuilder


class ExtractionsEdgeBuilder(AbstractEdgeBuilder):
    def __init__(self, extractions_file: str, verbose: bool = False) -> None:
        self.extractions_file = extractions_file
        self.verbose = verbose
        super().__init__()

    def read_edges_from_file(
        self,
        x_field: str,
        y_field: str,
        filename_field: str,
        matchspan_field: str,
    ) -> List[Tuple[str, str, dict]]:
        edges = defaultdict(list)
        with open(self.extractions_file, "r") as inf:
            msg = "[*] Building graph from {}".format(self.extractions_file)
            disable: bool = not self.verbose
            for serialized_extraction in tqdm(inf, desc=msg, disable=disable):
                serialized_extraction = json.loads(serialized_extraction)
                variable_x = serialized_extraction[x_field]
                variable_y = serialized_extraction[y_field]
                filename: str = serialized_extraction[filename_field]
                match_span: str = serialized_extraction[matchspan_field]
                match_snippet: str = self._get_snippet(
                    filename=filename,
                    match_span_field=serialized_extraction[matchspan_field],
                )  # noqa: E501
                data: dict = {
                    "filename": filename,
                    "snippet": match_snippet,
                    "match_charspan": match_span,
                }
                edges[(variable_x, variable_y)].append(data)
        out: List[Tuple[str, str, dict]] = []
        for vertex_names, edge_metadata in edges.items():
            u, v = vertex_names
            # edge metadata is stored as a list of dicts, but needs to be a
            # single dictionary for networkx so build a dict w/ keys for
            # each item in the list
            # maydo remove dependency on nx for serialization this is a mess
            # I guess you could use a graph DB? maybe networkx is fine.
            as_one_dict = {i: v for i, v in enumerate(edge_metadata)}
            out.append((u, v, as_one_dict))
        return out

    #  precomputing snippets here b/c not sure how to disribute abstracts
    def _get_snippet(
        self, match_span_field: List[int], filename: str, context: int = 100
    ) -> str:
        with open(filename, "r") as inf:
            txt: str = inf.read()
            start, end = match_span_field
            snippet: str = txt[start - context : end + context]
            return "..." + snippet + "..."


if __name__ == "__main":
    eb = ExtractionsEdgeBuilder("d")
