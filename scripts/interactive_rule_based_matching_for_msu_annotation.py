"""
Take data in the msu format and convert it to connl
"""

import json
from typing import Dict, List
from src.extractors.match_unpacker import MatchUnpacker
import numpy as np
import spacy
from numpy import ndarray
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span


def average_vectors(vectors: List[ndarray]) -> ndarray:
    return np.mean(vectors, axis=0)


def span2meanvector(span: Span) -> ndarray:
    return average_vectors([o.vector for o in span])  # type: ignore


def make_and_write_rules() -> None:
    '''
    Make rules for the rule-based system
    '''
    nlp = spacy.load("en_core_web_md")
    matcher = Matcher(nlp.vocab)

    print("[*] Running on annotated rain to start")

    # we instrument X with Y TODO

    # hack for groups in matcher => https://github.com/explosion/spaCy/discussions/9927 # noqa: 501

    # pattern = [{"LOWER": "effect"}, {"LOWER": "of"} + NP + {"LOWER": "on"} + NP] # noqa: 501

    # https://github.com/explosion/spaCy/blob/master/spacy/glossary.py
    NOUN_TAGS = ["NN", "NNP", "NNPS", "NNS"]
    ADJ_TAGS = ["ADJ"]
    PREP_TAGS = ["IN", "TO", "ADP"]

    adjective_or_noun = {"TAG": {"IN": NOUN_TAGS + ADJ_TAGS}, "OP": "*"}
    noun = {"tag": {"IN": NOUN_TAGS}}
    prep = {"tag": {"IN": PREP_TAGS}}
    det_star = {"tag": {"IN": PREP_TAGS}, "OP": "*"}

    effect_of: List = [
        {"LOWER": {"IN": ["effect", "impact"]}}, {"LOWER": "of"}]
    on: List = [{"LOWER": "on"}]
    to: List = [{"LOWER": "on"}]

    # (A|N)*N
    NP_short: List = [adjective_or_noun, noun]

    # (A|N)*N(PD*(A|N)*N)
    NP_long: List = NP_short + \
        [prep, det_star, adjective_or_noun, noun]

    # there are 4 ways to fill the NP slot
    # pattern = [{"LOWER": "effect"}, {"LOWER": "of"} + NP + {"LOWER": "on"} + NP] # noqa: 501
    # (A|N)*N, (A|N)*N
    # (A|N)*N, (A|N)*N(PD*(A|N)*N)
    # (A|N)*N(PD*(A|N)*N), (A|N)*N
    # (A|N)*N(PD*(A|N)*N), (A|N)*N(PD*(A|N)*N)

    # with open("config/rules/nps.json", "w") as of:
    #    r = {"name": "np1", "pattern": NP_short}
    #    of.write(json.dumps(r) + "\n")
    #    r = {"name": "np2", "pattern": NP_long}
    #    of.write(json.dumps(r) + "\n")

    with open("config/rules/effect_of_x_on_y.json", "w") as of:

        pattern = effect_of + NP_short + on + NP_short

        p1 = {"name": "effect_of_x_on_y_1", "pattern": pattern}
        of.write(json.dumps(p1) + "\n")

        matcher.add("E1", [pattern])

        pattern = effect_of + NP_long + on + NP_short
        p2 = {"name": "effect_of_x_on_y_2", "pattern": pattern}
        of.write(json.dumps(p2) + "\n")

        matcher.add("E2", [pattern])

        pattern = effect_of + NP_short + on + NP_long
        p3 = {"name": "effect_of_x_on_y_3", "pattern": pattern}
        of.write(json.dumps(p3) + "\n")
        matcher.add("E3", [pattern])

        pattern = effect_of + NP_long + on + NP_long
        p4 = {"name": "effect_of_x_on_y_4", "pattern": pattern}
        of.write(json.dumps(p4) + "\n")
        matcher.add("E4", [pattern])

        pattern = NP_short + [{"LOWER": "to"}, {"LOWER": "have"}, {"LOWER": "a"}]
        pattern = pattern + [{"LOWER": {"IN": ["positive", "negative"]}}]
        pattern = pattern + [{"LOWER": "effect"}, {"LOWER": "on"}] + NP_short
        matcher.add("E5", [pattern])
        p5 = {"name": "positive_effect_on", "pattern": pattern}
        of.write(json.dumps(p5) + "\n")
        # income gaps to have a positive/negative effect on hate crimes

    with open("config/rules/relationship_between_x_on_y.json", "w") as of:
        relationshipbetween = [{"LOWER": "relationship"}, {"LOWER": "between"}]
        and_ = [{"LOWER": "and"}]

        pattern = relationshipbetween + NP_short + and_ + NP_short
        p1 = {"name": "relationship_between_1", "pattern": pattern}
        of.write(json.dumps(p1) + "\n")
        matcher.add("R1", [pattern])

        pattern = relationshipbetween + NP_short + and_ + NP_long
        p2 = {"name": "relationship_between_2", "pattern": pattern}
        of.write(json.dumps(p2) + "\n")
        matcher.add("R2", [pattern])

        pattern = relationshipbetween + NP_long + and_ + NP_short
        p3 = {"name": "relationship_between_3", "pattern": pattern}
        of.write(json.dumps(p3) + "\n")
        matcher.add("R3", [pattern])

        pattern = relationshipbetween + NP_long + and_ + NP_long
        p4 = {"name": "relationship_between_4", "pattern": pattern}
        of.write(json.dumps(p4) + "\n")
        matcher.add("R4", [pattern])


def read_rules() -> list[Dict]:
    patterns: list[Dict] = []
    with open("config/rules/effect_of_x_on_y.json", "r") as inf:
        for i in inf:
            patterns.append(json.loads(i))
    with open("config/rules/relationship_between_x_on_y.json", "r") as inf:
        for i in inf:
            patterns.append(json.loads(i))
    return patterns


def get_docs():
    sent = []
    c = 0
    with open("data/msu/oren.conll", "r") as inf:
        for i in inf:
            if i != "\n":
                tok, tag = i.split("\t")
                sent.append(tok)
            else:
                doc = Doc(nlp.vocab, words=sent)
                doc = nlp(doc)
                filename = "data/msu/oren.conll"
                sent = []
                yield doc

def get_docs2():
    str_ = "Gale et al (2002) use American state-level data for 1992-1995 and find unemployment rates and black-white income gaps to have a positive effect on hate crimes committed by whites against blacks."
    yield nlp(str_)


if __name__ == "__main__":

    make_and_write_rules()
    nlp = spacy.load("en_core_web_md")
    matcher = Matcher(nlp.vocab)
    rules = read_rules()



    for rule in rules:
        matcher.add(rule["name"], [rule["pattern"]])

    unpacker = MatchUnpacker()

    sent = []
    c = 0
    for doc in get_docs2():
        matches = matcher(doc)
        sent = []

        for match_id, start, end in matches:

            # Get string representation
            match_kind = nlp.vocab.strings[match_id]
            match_span = doc[start:end]  # The matched match_span

            print(unpacker.match2variables(match_kind, match_span))
            print(match_span)