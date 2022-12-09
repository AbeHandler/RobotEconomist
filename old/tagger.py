import json

from src.corpus.corpus import Corpus
from src.corpus.loader import CorpusLoader
from src.corpus.paper import Paper
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Tag:
    '''
    This abstracts over output from Spacy. The reasons are
    1. Maybe you won't always use spacy
    2. You can test oracle taggers that perfectly recover training data
    '''
    origin_paper_id: str  # e.g. "doc1.jsonl"
    sentence_id: int  # e.g. 11
    literal_text: str  # e.g. "johnson.jsonl"
    tag: str  # e.g. "IV"
    confidence_score: float = 1  # e.g. 7, for networkx


class AbstractTagger(ABC):

    def __init__(self, config: str):
        super().__init__()
        with open(config, "r") as inf:
            self.config = json.load(inf)
        self.tagset = set(self.config["vertexes"].values())

    @abstractmethod
    def tag(self, corpus) -> List[Tag]:
        pass


class OracleConllTagger(AbstractTagger):

    '''
    Get oracle tags based on training data
    '''

    def ent2tag(self, ent, sentence_id, paper_id):
        first_in_tuple = ent[0]
        tag: str = first_in_tuple[0]
        tag: str = tag.split("-")[0]
        assert tag in self.tagset
        literal_text = " ".join([o[1] for o in ent])
        return Tag(paper_id, sentence_id, literal_text, tag)

    def tag_paper(self, paper: Paper, corpus_dir: str = "data/rain"):
        '''
        This method is included in part to ease testing and simplify tag method

        you need to include corpus_dir b/c it has the oracle files
        '''
        assert type(paper) == Paper
        paper_id = paper.paper_id
        paper_conll = paper_id.replace(".json", ".conll")
        sentence_id = 0
        _tags = []
        filetoread = corpus_dir + "/conll/" + paper_conll

        with open(filetoread, "r") as inf:
            last_ = ""
            ent = []
            for line_ in inf:
                line_ = line_.replace("\n", "")
                if line_ == "":
                    sentence_id += 1
                else:
                    word, label = line_.split("\t")

                    if label != "O" and label != "":
                        ent.append((label, word))
                    if label == "O" and len(ent) != 0:
                        _tags.append(self.ent2tag(
                            ent, sentence_id, paper_id))
                        ent = []
        return _tags

    def tag(self, corpus: Corpus, corpus_dir: str = "data/rain") -> List[Tag]:
        tags: List[Tag] = []

        for paper in corpus.papers:
            try:
                assert type(paper) == Paper
                tags = tags + self.tag_paper(paper, corpus_dir)
            except FileNotFoundError:  # this can lead to sneaky bugs if corpus_dir is wrong TODO
                # try setting corpus_dir to garbage, all the tests will fail b/c there are no files to get tags
                # probably not worth fixing but noting here
                pass  # not all files in corpus are tagged in appendix A
        return tags


class OracleConllTaggerRain(OracleConllTagger):

    '''run oracle tagger for Mellon (2021), where we know weather is the IV'''

    def tag(self, corpus, corpus_dir: str = "data/rain") -> List[Tag]:
        tags = super().tag(corpus)
        for tag in tags:
            paper_id = tag.origin_paper_id
            if tag.tag == self.config["vertexes"]["regressor"]:
                instrument = self.config["vertexes"]["instrument"]
                tags.append(Tag(paper_id, sentence_id=tag.sentence_id,
                            literal_text="weather", tag=instrument))
        return tags


class SpacyTagger(AbstractTagger):

    def tag(self, corpus) -> List[Tag]:
        raise NotImplementedError("write me")


if __name__ == "__main__":
    loader = CorpusLoader("data/rain")
    corpus = loader.load_corpus()
    with open("config/config.json", "r") as inf:
        config = json.load(inf)
    tagset = set(config["vertexes"].values())
    tagger = OracleConllTagger(config="config/config.json")
    tags = tagger.tag(corpus)
    print(tags)
