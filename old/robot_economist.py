import json

from src.dag.dag import Dag
from src.dag.auditor import Auditor
from src.tagger import AbstractTagger, OracleConllTaggerRain
from src.corpus.corpus import Corpus
from src.corpus.loader import CorpusLoader
from src.tagger import Tag
from src.graph_builder import GraphBuilder
from typing import List


class RobotEconomist(object):

    def __init__(self, tagger: AbstractTagger, corpus: Corpus, config: str = "config.json"):
        self.config = config
        self.tagger = tagger
        self.corpus = corpus

    def make_dag(self) -> Dag:
        tags: List[Tag] = self.tagger.tag(self.corpus)
        analyzer = GraphBuilder(self.corpus)
        dag: Dag = analyzer.tags_to_dag(tags)
        return dag


if __name__ == "__main__":

    loader = CorpusLoader()
    corpus = loader.load_corpus()
    tagger = OracleConllTaggerRain(config="config.json")

    robot = RobotEconomist(config="config.json",
                           tagger=tagger,
                           corpus=corpus)
    dag = robot.make_dag()

    auditor = Auditor(dag)

    weather = next(i for i in dag.vertexes if i.variable_name == "weather")

    for paper in corpus.papers:
        try:
            tags = tagger.tag_paper(paper, corpus_dir="data/rain")
            if len(tags) > 0 and any(j.tag == 'Y' for j in tags):
                outcome = next(j for j in tags if j.tag == 'Y')
                sink = next(
                    j for j in dag.vertexes if j.variable_name == outcome.literal_text)
                if not auditor.is_kosher(weather, sink):
                    print("\n[*] Auditing {}".format(paper.paper_id))
                    print("- The outcome is {}".format(outcome.literal_text))
                    auditor.audit(weather, sink, verbose=True)
        except FileNotFoundError:
            pass

        #auditor.audit(source, sink)
