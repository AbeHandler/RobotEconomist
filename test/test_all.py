import unittest
from pathlib import Path

from networkx import DiGraph
from numpy import ediff1d

from src.audit.auditor import Auditor
from src.graph.edges.effects_edge import EffectsEdge
from src.graph.path import Path as DagPath
from src.graph.vertex import Vertex
from src.graph_builders.extractions_to_networkx import (  # noqa: E501
    Extractions2NetworkXConverter,
)
from src.pipelines.pipeline_config import PipelineConfig


class TestMethods(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_test_one(self) -> None:
        self.assertTrue(1 < 2)

    def test_extractions_2_networkx_has_filenames(self) -> None:
        corpus = "nber_abstracts"
        config: PipelineConfig = PipelineConfig(
            corpus=corpus, use_semantic_similarities=False
        )
        config.extractions_path = Path("test", "fixtures", "multi_edges.jsonl")
        graph_builder = Extractions2NetworkXConverter(
            config=config, verbose=False
        )

        G: DiGraph = graph_builder._build_graph()

        for edge in G.edges.data():
            x, y, data = edge
            for k in data.keys():
                self.assertTrue("filename" in data[k])

    def test_graph_has_filenames(self) -> None:

        corpus = "nber_abstracts"
        config: PipelineConfig = PipelineConfig(corpus=corpus)

        config.extractions_path = Path(
            "test", "fixtures", "nber.rulebased.extractions.jsonl"
        )
        graph_builder = Extractions2NetworkXConverter(
            config=config, verbose=False
        )
        graph_builder.build_and_serialize()

        path_to_graph: str = "data/nber_abstracts/graphs/rulebased.extractions.jsonl.nxdigraph.json"
        auditor = Auditor(graph_specification=path_to_graph)
        G: DiGraph = auditor._load_graph(path_to_graph)

        for edge in G.edges.data():
            x, y, data = edge
            self.assertTrue("filename" in data)

    def test_multiedges(self) -> None:
        corpus = "nber_abstracts"
        config: PipelineConfig = PipelineConfig(
            corpus=corpus, use_semantic_similarities=False
        )
        config.extractions_path = Path("test", "fixtures", "multi_edges.jsonl")
        graph_builder = Extractions2NetworkXConverter(
            config=config, verbose=False
        )
        G = graph_builder._build_graph()
        # there are 5 papers in the fixture that show a connection between
        # satisfaction and loyalty. They should all be recorded in the graph
        assert len(G.get_edge_data("satisfaction", "loyalty").keys()) == 5

        edges = graph_builder._get_edges()

        msg = f"Expected 2 edges found {len(edges)}"
        assert type(edges) == list, "expected a list"
        assert len(edges) == 2, msg

    def test_can_build_effects_edge(self) -> None:
        e = EffectsEdge(
            Vertex("a"), Vertex("b"), {"1": {"filename": "e", "snippet": "s"}}
        )
        assert len(e.data.keys()) == 1

    def test_can_build_path(self) -> None:
        v1 = Vertex("a")
        v2 = Vertex("b")
        e = EffectsEdge(v1, v2, {"1": {"filename": "e", "snippet": "s"}})
        p = DagPath(vertexes=[v1, v2], edges=[e])  # renamed b/c pathlib Path
        assert len(p.get_vertex_names()) == 2

    def test_path_edge_report_1(self) -> None:
        v1 = Vertex("a")
        v2 = Vertex("b")
        e = EffectsEdge(v1, v2, {"1": {"filename": "e", "snippet": "s"}})
        p = DagPath(vertexes=[v1, v2], edges=[e])  # renamed b/c pathlib Path
        assert p.get_edge_size_report() == "a--(1)-->b"

    def test_path_edge_report_2(self) -> None:
        v1 = Vertex("a")
        v2 = Vertex("b")
        v3 = Vertex("c")
        e = EffectsEdge(v1, v2, {"0": {"filename": "e", "snippet": "s"}})
        e2 = EffectsEdge(
            v2,
            v3,
            {
                "0": {"filename": "e", "snippet": "s"},
                "1": {"filename": "e", "snippet": "s"},
            },
        )
        p = DagPath(
            vertexes=[v1, v2, v3], edges=[e, e2]
        )  # renamed b/c pathlib Path
        assert p.get_edge_size_report() == "a--(1)-->b--(2)-->c"


if __name__ == "__main__":
    unittest.main()
