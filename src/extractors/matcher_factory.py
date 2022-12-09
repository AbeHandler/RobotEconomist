import json
from enum import Enum
from typing import Dict, List, NamedTuple

from spacy.matcher import Matcher
from spacy.vocab import Vocab

from src.pipelines.pipeline_config import PipelineConfig


class Rule(NamedTuple):
    rule: List[dict]
    rule_name: str


class MatchKind(Enum):
    iv: str = "iv"
    np: str = "np"
    outcome: str = "outcome"


class MatcherFactory(object):

    def __init__(self, vocab: Vocab) -> None:
        self.vocab = vocab

    def get_matcher(self, kind: MatchKind) -> Matcher:

        if not isinstance(kind, MatchKind):
            raise TypeError('Input must be a match kind')

        if kind.name == "iv":
            return self._get_iv_matcher()
        if kind.name == "np":
            return self._get_np_matcher()
        if kind.name == "outcome":
            return self._get_outcome_matcher()
        raise AttributeError('The matcher must by iv or np or outcome')

    def get_matcher_from_rules(self, paths_to_rules: List[str]) -> Matcher:
        '''
        Make a matcher from rules files

        Seems better to have this as a different method from the
        get_matcher method which takes a MatchKind
        '''
        matcher = Matcher(self.vocab)

        for rule in self._read_rules(paths_to_rules):
            matcher.add(rule["name"], [rule["pattern"]])

        return matcher

    def _read_rules(self,
                    _paths_to_rules: List[str]) -> list[Dict]:
        '''
        It is possible to serialize spacy rules in jsonl files
        This method reads those rules from disk to make a matcher
        Usually you make the rules interactively
        e.g. scripts/interactive_rule_based_matching.py
        '''
        patterns: list[Dict] = []
        for rule_file in _paths_to_rules:
            with open(rule_file, "r") as inf:
                for i in inf:
                    patterns.append(json.loads(i))

        return patterns

    def _get_np_rules(self) -> List[Rule]:
        NOUN_TAGS = ["NN", "NNP", "NNPS", "NNS"]
        ADJ_TAGS = ["ADJ"]
        PREP_TAGS = ["IN", "TO", "ADP"]

        adjective_or_noun = {"TAG": {"IN": NOUN_TAGS + ADJ_TAGS}, "OP": "*"}
        noun = {"tag": {"IN": NOUN_TAGS}}
        prep = {"tag": {"IN": PREP_TAGS}}
        det_star = {"tag": {"IN": PREP_TAGS}, "OP": "*"}

        # (A|N)*N
        NP_short: List = [adjective_or_noun, noun]

        # (A|N)*N(PD*(A|N)*N)
        NP_long: List = NP_short + \
            [prep, det_star, adjective_or_noun, noun]

        return [Rule(NP_short, "NP_s"), Rule(NP_long, "NP_l")]

    def _get_iv_rules(self) -> List[Rule]:
        rules: List[Rule] = [Rule([{"LOWER": "instrumental"},
                                   {"LOWER": "variable"}], "IV")]
        rules.append(Rule([{"LOWER": "instrument"}], "IV2"))
        return rules

    def _get_outcome_rules(self) -> List[Rule]:
        '''
        Roughly 1/4 outcome variables in initial MSU annotation are within
        a few tokens of the word effect
        '''
        rules: List[Rule] = [Rule([{"LOWER": "effect"}], "OUTCOME")]
        return rules

    def _get_iv_matcher(self) -> Matcher:
        rules: List[Rule] = self._get_iv_rules()
        return self._build_matcher(rules=rules)

    def _get_outcome_matcher(self) -> Matcher:
        rules: List[Rule] = self._get_outcome_rules()
        return self._build_matcher(rules=rules)

    def _get_np_matcher(self) -> Matcher:
        rules: List[Rule] = self._get_np_rules()
        return self._build_matcher(rules=rules)

    def _build_matcher(self, rules: List[Rule]) -> Matcher:
        matcher = Matcher(self.vocab)

        for rule in rules:
            matcher.add(rule.rule_name, [rule.rule])

        return matcher


if __name__ == "__main__":
    config: PipelineConfig = PipelineConfig(corpus="nber")
    factory = MatcherFactory(config.vocab)
    matcher: Matcher = factory.get_matcher(kind=MatchKind.iv)