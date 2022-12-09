import json
from typing import List, Tuple

from tqdm import tqdm as tqdm

from src.graph_builders.edge_builders.abstract_edge_builder import (  # noqa: E501
    AbstractEdgeBuilder,
)


class SimilaritiesEdgeBuilder(AbstractEdgeBuilder):

    def __init__(self, semantics_file: str, verbose: bool = False) -> None:
        self.semantics_file = semantics_file
        self.verbose = verbose
        super().__init__()

    def read_edges_from_file(self, **kwargs: dict) -> List[dict]:
        edges: List[Tuple] = []
        print("?")
        with open(self.semantics_file, "r") as inf:
            msg = "[*] Building edges from {}".format(self.semantics_file)
            disable: bool = not self.verbose
            for serialized_extraction in tqdm(inf, desc=msg, disable=disable):
                serialized_extraction = json.loads(serialized_extraction)
                variable_x: str = serialized_extraction["term1"]
                variable_y: str = serialized_extraction["term2"]
                distance: float = float(serialized_extraction["distance"])
                match_snippet = f"distance {distance}"
                data: dict = {"filename": 'NA',
                              "distance": distance,
                              "snippet": match_snippet,
                              "match_charspan": "NA"}
                edges.append((variable_y, variable_x, data))  # similarity is bi directional
                edges.append((variable_x, variable_y, data))  # similarity is bi directional
        return edges

    #  precomputing snippets here b/c not sure how to disribute abstracts
    def _get_snippet(self,
                     match_span_field: List[int],
                     filename: str,
                     context: int = 100) -> str:
        with open(filename, "r") as inf:
            txt: str = inf.read()
            start, end = match_span_field
            snippet: str = txt[start - context: end + context]
            return "..." + snippet + "..."


if __name__ == "__main__":
    eb = SimilaritiesEdgeBuilder("data/s2orc_abstracts/similarities/similarities.jsonl", verbose=True)
    eb.read_edges_from_file()