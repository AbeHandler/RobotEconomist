from glob import glob
from src.corpus.corpus import Corpus
from src.corpus.section import Section
from src.corpus.paper import Paper
import json


class CorpusLoader(object):

    def __init__(self, dir_="data/rain", corpus_id=None):
        self.dir = dir_
        self.filenames = self.get_file_names()
        self.corpus_id = self.dir if corpus_id is None else corpus_id

    def get_file_names(self, extension="json"):
        '''
        Return file names from a directory in alphabetical order
        '''
        names = [o for o in glob(self.dir + "/" + "*" + extension)]
        names.sort()
        return names

    def load_corpus(self) -> Corpus:

        papers = []
        for filename in self.filenames:
            with open(filename, "r") as inf:
                dt = json.load(inf)
                sections = []
                for title in dt.keys():
                    id_ = filename.split("/").pop()
                    title = Section(title, dt[title], id_)
                    sections.append(title)
                paper = Paper(id_, sections)
                papers.append(paper)
        return Corpus(self.corpus_id, papers)
