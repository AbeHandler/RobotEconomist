from itertools import product
from typing import List, Tuple

from spacy.tokens import Doc

from src.audit.abstract_possible_violation import PossibleViolation
from src.audit.auditor import Auditor
from src.extractors.abstract_extractor import AbstractExtractor
from src.extractors.extraction import Extraction


class ViolationHunter(object):
    """
    Finds and reasons about possible violations
    """

    def __init__(
        self,
        auditor: Auditor,
        extractor: AbstractExtractor,
        exclude_semantic_only_paths: bool = True,
        distance_threshold: float = 100,
        min_edges: int = 2,
    ) -> None:
        self.extractor = extractor
        self.auditor = auditor
        self.exclude_semantic_only_paths = exclude_semantic_only_paths
        self.distance_threshold = distance_threshold
        self.min_edges = min_edges

    def get_possible_violations(self, doc: Doc) -> List[PossibleViolation]:
        output: List[PossibleViolation] = []
        for instrument, outcome in self._get_candidates(doc):
            try:
                if self.auditor.has_iv_violation(
                    proposed_instrument=instrument.text_of_extraction,  # noqa: E501
                    proposed_outcome=outcome.text_of_extraction,
                ):  # noqa: E501
                    violation = self.auditor.get_possible_violation(
                        instrument=instrument, outcome=outcome  # noqa: E501
                    )  # noqa: E501
                    output.append(violation)
            except AttributeError:
                pass  # thrown if variable is not known to auditor

        if self.exclude_semantic_only_paths:
            output = self._filter_out_only_semantic(output)

        output = self._filter_below_distance_threshold(output)

        output = [o for o in output if len(o.path.edges) > self.min_edges]
        return output

    def _get_candidates(self, doc: Doc) -> List[Tuple[Extraction, Extraction]]:

        ivs: List[Extraction] = self.extractor.get_instruments(doc)

        outcomes: List[Extraction] = self.extractor.get_outcomes(doc)

        all_pairs: List[Tuple[Extraction, Extraction]] = []
        for instrument, outcome in product(ivs, outcomes):
            # compare equality on text of extraction below
            # you can get two extractions of same words in same doc in diff
            # locations. so if you do a simple __eq__ then they are different
            # but we want something stricter.
            if instrument.text_of_extraction != outcome.text_of_extraction:
                all_pairs.append((instrument, outcome))

        return all_pairs

    def _filter_below_distance_threshold(
        self, violations: List[PossibleViolation]
    ) -> List[PossibleViolation]:
        out: List[PossibleViolation] = []
        for violation in violations:
            if violation.max_semantic_distance() < self.distance_threshold:
                out.append(violation)
        return out

    def _filter_out_only_semantic(
        self, violations: List[PossibleViolation]
    ) -> List[PossibleViolation]:
        out: List[PossibleViolation] = []
        for violation in violations:
            if not violation.is_only_semantic():
                out.append(violation)
        return out
