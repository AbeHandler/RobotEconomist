import re
from typing import Optional
import spacy
import json
import glob

from spacy.tokens import Span
from src.corpus.corpus import Corpus
from src.corpus.loader import CorpusLoader
from src.corpus.paper import Paper
from src.corpus.section import Section
from src.experiments.mellon import AppendixA

END_SENTENCE = ("", "")


def get_section(paper, section="abstract") -> Section:
    for section in paper.sections:
        if section.title.lower() == "abstract":
            return section
    raise RuntimeError(
        "Section {} in paper {} was not found".format(section, paper.paper_id))


def get_span_from_string(str_: str, doc) -> Optional[Span]:
    '''
    checks to see if string is a span in a spacy doc
    checks uppercase and lowercase
    '''

    # TODO this needs to handle no retturn not in string
    for match in re.finditer(str_.lower(), doc.text):
        start, end = match.span()
        span = doc.char_span(start, end)
        return span

    for match in re.finditer(str_, doc.text):
        start, end = match.span()
        span = doc.char_span(start, end)
        return span


def spacy_span_to_token_range(span: Span) -> list:
    if span is None:
        return []
    else:
        return list(range(span[0].i, span[-1].i + 1))


def get_conll_labels_for_tokens(_doc, yspan_abstract_range, xspan_abstract_range) -> list:
    out = []

    for sent in _doc.sents:
        for token in sent:
            word = str(token)
            index = token.i
            label = "O"
            if index in yspan_abstract_range:
                if index == yspan_abstract_range[0]:
                    label = "Y-I"
                else:
                    label = "Y-B"
            if index in xspan_abstract_range:
                if index == xspan_abstract_range[0]:
                    label = "X-I"
                else:
                    label = "X-B"
            out.append((word, label))

        # for sentence segmentation
        out.append(END_SENTENCE)
    return out


def conll_write_helper(filename: str, out: list) -> None:
    with open(filename, "w") as of:
        for o in out:
            assert type(o) == tuple
            assert len(o) == 2
            if o != END_SENTENCE:
                of.write("\t".join(o) + "\n")
            else:
                of.write("\n")


def write_out_paper(out: list,
                    training_dir: str = "data/rain/conll/",
                    section: str = "abstract",
                    paper_id: str = "paper.json",
                    output_extension: str = "conll") -> None:
    paper_id = paper_id.replace(".json", ".{}.conll".format(section))
    conll_write_helper(training_dir + paper_id, out)


def write_out_all(out,
                  training_dir="data/rain/conll/",
                  paper_id="all.conll",
                  output_extension="conll") -> None:
    conll_write_helper(training_dir + paper_id, out)


def paper_section_to_conll(paper: Paper,
                           section="abstract",
                           nlp=None,
                           X=None,
                           Y=None) -> list:
    section = get_section(paper, section)
    section_doc = nlp(section.text)
    xspan = get_span_from_string(X, section_doc)
    yspan = get_span_from_string(Y, section_doc)
    xspan_range = spacy_span_to_token_range(xspan)
    yspan_range = spacy_span_to_token_range(yspan)
    return get_conll_labels_for_tokens(section_doc, yspan_range, xspan_range)


def make_training_data_from_mellon() -> None:
    nlp = spacy.load("en_core_web_sm")
    # %%
    appendix = AppendixA()

    loader = CorpusLoader("data/rain")

    papers = loader.load_corpus()

    # not all apers are in the appendix
    papers = [o for o in papers if o.paper_id in appendix.papers]
    loader = CorpusLoader("mellon")  # this is a bug #TODO if needed
    corpus = loader.load_corpus()
    everything: list = []

    def clean(paper_id):
        if "Collins" in paper_id:
            return False
        if "Hornbeck" in paper_id:
            return False
        if "Luechinger" in paper_id:
            return False
        return True

    papers = [o for o in papers if clean(o.paper_id)]

    for paper in papers:

        X = appendix.get_X(paper.paper_id)
        Y = appendix.get_Y(paper.paper_id)

        abstract = paper_section_to_conll(
            paper, section="abstract", nlp=nlp, X=X, Y=Y)
        write_out_paper(abstract, paper_id=paper.paper_id, section="abstract")
        everything = everything + abstract

        intro = paper_section_to_conll(
            paper, section="introduction", nlp=nlp, X=X, Y=Y)
        everything = everything + intro

        paper_as_conll = abstract + intro

        out_id = paper.paper_id.replace('.json', '.conll')
        write_out_all(paper_as_conll, paper_id=out_id)

    write_out_all(everything)


if __name__ == "__main__":
    make_training_data_from_mellon()
