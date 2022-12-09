from re import I
import unittest
import spacy
import json
from typing import Dict, List
from src.dag.dag import Dag
from src.dag.auditor import Auditor
from src.dag.printer import Printer
from src.dag.vertex import Vertex
from src.dag.edge import Edge
from src.robot_economist import RobotEconomist
from src.tagger import Tag, OracleConllTagger, OracleConllTaggerRain, SpacyTagger
from src.corpus.corpus import Corpus
from src.corpus.loader import CorpusLoader
from src.corpus.paper import Paper
from src.graph_builder import AbstractTagCluster, GraphBuilder


class TestMethods(unittest.TestCase):

    def setUp(self) -> None:
        v1 = Vertex("weather", "demo.json", 1)
        v2 = Vertex("income", "demo.json", 2)
        self.V = [v1, v2]
        self.e = [Edge(v1, v2, "affects")]
        with open("config/config.json", "r") as inf:
            self.config = json.load(inf)

    def test_load_tiny_spacy_model(self) -> None:
        nlp = spacy.load("test/fixtures/tiny_pipeline/model-last")

    def test_dag_auditor_created(self) -> None:
        dag = Dag(vertexes=self.V, edges=self.e)
        auditor = Auditor(dag)
        self.assertEqual(type(auditor), Auditor)

    def test_dag_printer_created(self) -> None:
        dag = Dag(vertexes=self.V, edges=self.e)
        printer = Printer(dag)
        self.assertEqual(1, 1)

    def test_dag_printer_runs(self) -> None:
        dag = Dag(vertexes=self.V, edges=self.e)
        printer = Printer(dag, output_filename="/tmp/dag.pdf")
        self.assertEqual(1, 1)

    def test_fig_1_good(self) -> None:
        '''
        The instrumental variable example from Mellon's figure 1
        that is good should be kosher according to the auditor
        '''
        w = Vertex("W", "demo.json", 1)
        u = Vertex("U", "demo.json", 2)
        x = Vertex("X", "demo.json", 3)
        y = Vertex("Y", "demo.json", 4)

        E = {Edge(w, x, "instruments"),
             Edge(x, y),
             Edge(u, x),
             Edge(u, y)}
        dag = Dag(vertexes=[w, u, x, y], edges=E)
        auditor = Auditor(dag)
        self.assertTrue(auditor.is_kosher(source=w, sink=y))

    def test_fig_1_bad(self) -> None:

        w = Vertex("W", "demo.json", 1)
        u = Vertex("U", "demo.json", 2)
        x = Vertex("X", "demo.json", 3)
        y = Vertex("Y", "demo.json", 4)
        z = Vertex("Z", "demo.json", 5)

        E = {Edge(w, x, "instruments"),
             Edge(w, z),
             Edge(u, x),
             Edge(u, y),
             Edge(u, z),
             Edge(z, y),
             Edge(x, y)}
        dag = Dag(vertexes=[w, u, x, y], edges=E)
        auditor = Auditor(dag)
        self.assertFalse(auditor.is_kosher(source=w, sink=y))

    def test_classes_run_together(self) -> None:

        loader = CorpusLoader()
        corpus = loader.load_corpus()
        robot = RobotEconomist(config="config/config.json",
                               tagger=OracleConllTagger(
                                   config="config/config.json"),
                               corpus=corpus)
        dag = robot.make_dag()
        auditor = Auditor(dag)
        a = dag.vertexes[0]
        b = dag.vertexes[1]
        auditor.audit(source=a, sink=b)

    def test_oracle_tagger_rain_one_paper(self) -> None:
        loader = CorpusLoader("data/rain")
        corpus = loader.load_corpus()
        assert type(corpus) == Corpus
        tagger = OracleConllTaggerRain(config="config/config.json")
        paper = next(o for o in corpus.papers if "Vahedi" in o.paper_id)
        tags = tagger.tag_paper(paper, corpus_dir="data/rain")
        tags = set([o.tag for o in tags])
        assert "X" in tags

    def test_oracle_tagger_rain_whole_corpus(self) -> None:
        loader = CorpusLoader("data/rain")
        corpus = loader.load_corpus()
        assert type(corpus) == Corpus
        tagger = OracleConllTaggerRain(config="config/config.json")
        tags = tagger.tag(corpus)
        print(tags)
        tags = set([o.tag for o in tags])
        assert "IV" in tags

    def test_corpus_loads_mini_fixtures(self) -> None:
        loader = CorpusLoader("test/fixtures/mini")
        corpus = loader.load_corpus()
        assert len(loader.filenames) == 3

    def test_oracle_tagger_loads_and_runs(self) -> None:
        loader = CorpusLoader("test/fixtures/mini")
        corpus = loader.load_corpus()
        tagger = OracleConllTagger(config="config/config.json")
        tags: List[Tag] = tagger.tag(corpus)  # can tag

    def test_oracle_tagger_gets_paper_tags(self) -> None:
        loader = CorpusLoader("test/fixtures/mini")
        corpus = loader.load_corpus()
        tagger = OracleConllTagger(config="config/config.json")
        paper = next(j for j in corpus.papers if j.paper_id == "doc2.json")
        tags: List[Tag] = tagger.tag_paper(
            paper, "test/fixtures/mini")  # can tag
        assert len(tags) == 4
        assert sum(1 for i in tags if i.tag == "X") == 2
        assert sum(1 for i in tags if i.tag == "Y") == 1
        tag_names = set(i.tag for i in tags)
        assert "X" in set(tag_names)
        assert "Y" in set(tag_names)
        assert "IV" in set(tag_names)
        assert len(tag_names) == 3

    def test_analyzer_dedupes_vertexes(self) -> None:
        '''
        tests/fixtures/mini/dag.jpeg has a picture of the dag
        '''
        loader = CorpusLoader("test/fixtures/mini")
        corpus = loader.load_corpus()
        tagger = OracleConllTagger(config="config/config.json")
        tags = tagger.tag(corpus, corpus_dir="test/fixtures/mini")
        assert len(tags) > 0
        analyzer = GraphBuilder(corpus)
        clusters = analyzer.vertex_coref_resolver.clusterN_squared(
            tags)
        vertexes: List[Vertex] = list(
            analyzer.clusters_to_vertexes(clusters).values())
        assert len(vertexes) == 4
        weather: Vertex = next(
            i for i in vertexes if i.variable_name == "weather")
        mood: Vertex = next(
            i for i in vertexes if i.variable_name == "mood")
        income: Vertex = next(
            i for i in vertexes if i.variable_name == "income")
        assert "doc1.json" in weather.papers_id and "doc2.json" in weather.papers_id
        assert "doc1.json" in weather.papers_id and "doc3.json" in mood.papers_id
        assert "doc1.json" in weather.papers_id and "doc2.json" in income.papers_id

    def test_analyzer_edges_on_mini_corpus(self) -> None:
        '''
        tests/fixtures/mini/dag.jpeg has a picture of the dag
        '''
        loader = CorpusLoader("test/fixtures/mini")
        corpus = loader.load_corpus()
        tagger = OracleConllTagger(config="config/config.json")
        tags = tagger.tag(corpus, corpus_dir="test/fixtures/mini")
        analyzer = GraphBuilder(corpus)
        clusters = analyzer.vertex_coref_resolver.clusterN_squared(
            tags)
        cluster2vertex: Dict[AbstractTagCluster,
                             Vertex] = analyzer.clusters_to_vertexes(clusters)

        edges = analyzer.impute_edges_corpus(clusters, cluster2vertex)
        assert len(clusters) == 4
        assert len(cluster2vertex.keys()) == 4
        names = set([v.variable_name for v in cluster2vertex.values()])
        assert names == set(["weather", "mood", "income", "voting"])
        assert len(edges) == 5
        e1 = sum(1 for i in edges if i.A.variable_name ==
                 "mood" and i.B.variable_name == "income")
        assert e1 == 1
        print("?")

    def test_analyzer_edges_on_mini_corpus_one_edge(self) -> None:
        '''
        tests/fixtures/mini/dag.jpeg has a picture of the dag
        '''
        loader = CorpusLoader("test/fixtures/mini")
        corpus = loader.load_corpus()
        tagger = OracleConllTagger(config="config/config.json")
        tags = tagger.tag(corpus)
        analyzer = GraphBuilder(corpus)
        clusters = analyzer.vertex_coref_resolver.clusterN_squared(
            tags)
        cluster2vertex: Dict[AbstractTagCluster,
                             Vertex] = analyzer.clusters_to_vertexes(clusters)
        edges = analyzer.impute_edges_corpus(clusters, cluster2vertex)

        # reduce doen to one edge
        cluster2vertex = {k: v for k, v in cluster2vertex.items() if v.variable_name in [
            "voting", "income"]}
        clusters = list(cluster2vertex.keys())
        edges = analyzer.impute_edges_corpus(clusters, cluster2vertex)
        assert len(edges) == 1

    def test_robot_economist_on_mini_corpus(self) -> None:
        '''
        tests/fixtures/mini/dag.jpeg has a picture of the dag
        '''
        loader = CorpusLoader("test/fixtures/mini")
        corpus = loader.load_corpus()
        tagger = OracleConllTagger(config="config/config.json")
        robot = RobotEconomist(config="config/config.json",
                               tagger=tagger,
                               corpus=corpus)
        dag = robot.make_dag()
        w = next(o for o in dag.vertexes if o.variable_name == "weather")
        y = next(o for o in dag.vertexes if o.variable_name == "income")
        auditor = Auditor(dag)
        self.assertFalse(auditor.is_kosher(source=w, sink=y))
        auditor.audit(source=w, sink=y, verbose=True)


if __name__ == '__main__':
    unittest.main()
