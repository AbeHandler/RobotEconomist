import json
import os
from pathlib import Path
from typing import List, Tuple

import networkx as nx
from networkx import DiGraph, node_link_graph

from src.graph_builders.edge_builders.abstract_edge_builder import (  # noqa: E501
    AbstractEdgeBuilder,
)
from src.graph_builders.edge_builders.extractions_edge_builder import (
    ExtractionsEdgeBuilder,
)
from src.graph_builders.edge_builders.similarities_edge_builder import (
    SimilaritiesEdgeBuilder,
)
from src.pipelines.pipeline_config import PipelineConfig


class Extractions2NetworkXConverter(object):
    """
    A simple graph builder that translates from one or more
    extractions or semantics files into a networkx graph

    Sep 12, 2022
    There is also stuff in old/src/graph_builder but it has a bunch
    of logic/abstractions that we may not need so doing a rewrite
    """

    def __init__(self, config: PipelineConfig, verbose: bool = False) -> None:

        self.extractions_file = config.extractions_path.as_posix()

        self.output_directory = Path(
            config.data_dir, config.corpus, config.graphs_dir
        ).as_posix()

        self.verbose = verbose
        self.edge_builders: List[AbstractEdgeBuilder] = []
        edge_builder: ExtractionsEdgeBuilder = ExtractionsEdgeBuilder(
            self.extractions_file
        )  # noqa: E501
        self.edge_builders.append(edge_builder)

        if config.use_semantic_similarities:
            self.similarities_file = Path(
                config.data_dir,
                config.corpus,
                config.similarities_dir,
                config.similarities_basename,
            ).as_posix()
            semantic_edge_builder: SimilaritiesEdgeBuilder = (
                SimilaritiesEdgeBuilder(self.similarities_file)
            )
            self.edge_builders.append(semantic_edge_builder)

    def build_and_serialize(self, verbose: bool = False) -> None:
        G: DiGraph = self._build_graph(verbose=verbose)
        self._serialize_graph(G)
        if self.verbose:
            output: str = self._get_cached_name(
                file_name=self.extractions_file
            )  # noqa: E501
            print(f"[*] Wrote to {output}")

    def _get_cached_name(
        self,
        file_name: str,
        extension: str = "nxdigraph.json",
    ) -> str:

        basename: str = os.path.basename(file_name)
        output_path: str = os.path.join(self.output_directory, basename)
        return output_path + "." + extension

    def _serialize_graph(self, G: DiGraph) -> None:
        output_path: str = self._get_cached_name(
            file_name=self.extractions_file
        )  # noqa: E501
        with open(output_path, "w") as of:
            json.dump(nx.node_link_data(G), of)

    def _get_edges(
        self,
        x_field: str = "variable_x",
        y_field: str = "variable_y",
        filename_field: str = "filename",
        matchspan_field: str = "match_charspan",
        verbose: bool = False,
    ) -> List[Tuple[str, str, dict]]:
        edges: List[Tuple[str, str, dict]] = []
        for edge_builder in self.edge_builders:
            edges = edges + edge_builder.read_edges_from_file(
                x_field=x_field,
                y_field=y_field,
                filename_field=filename_field,  # noqa: E501
                matchspan_field=matchspan_field,
            )  # noqa: E501
        return edges

    def _build_graph(
        self,
        x_field: str = "variable_x",
        y_field: str = "variable_y",
        filename_field: str = "filename",
        matchspan_field: str = "match_charspan",
        verbose: bool = False,
    ) -> DiGraph:

        edges = self._get_edges(
            x_field=x_field,
            y_field=y_field,
            filename_field=filename_field,
            matchspan_field=matchspan_field,
            verbose=verbose,
        )
        graph = nx.DiGraph()
        graph.add_edges_from(edges)
        return graph

    def _load_graph(self) -> DiGraph:
        output_path: str = self._get_cached_name(self.extractions_file)
        with open(output_path, "r") as inf:
            graph: dict = json.load(inf)
        return node_link_graph(graph)


if __name__ == "__main__":
    config = PipelineConfig(corpus="s2orcfull")
    config.use_semantic_similarities = False
    converter = Extractions2NetworkXConverter(config=config, verbose=True)
    converter.build_and_serialize()
