from typing import List

from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy.tokens.doc import Doc
from spacy.vocab import Vocab

from src.extractors.abstract_extractor import AbstractExtractor
from src.extractors.extraction import Extraction
from src.extractors.matcher_factory import MatcherFactory, MatchKind  # noqa: E501


class HeuristicExtractor(AbstractExtractor):
    '''
    A template class for heuristic extraction from documents

    Used to heuristically extract IVs and outcome variables
    '''

    def __init__(self,
                 vocab: Vocab,
                 K: int = 20
                 ) -> None:
        super().__init__()
        self.vocab = vocab
        self.K = K

    def get_instruments(self, doc: Doc) -> List[Extraction]:
        return self._get_extractions(MatchKind.iv, doc)

    def get_outcomes(self, doc: Doc) -> List[Extraction]:
        return self._get_extractions(MatchKind.outcome, doc)

    def _get_matching_indexes_in_doc(self,
                                     doc: Doc,
                                     matcher: Matcher) -> List[int]:
        matches = matcher(doc)
        out: List[int] = []
        for match_id, start, end in matches:
            for i in range(start, end):
                out.append(i)
        return out

    def _within_K(self,
                  word_index: int,
                  target_indexes: List[int]) -> bool:
        for target_index in target_indexes:
            if (target_index - self.K) < word_index < (target_index + self.K):
                return True
        return False

    def _get_extractions(self,
                         kind_of_index_to_find: MatchKind,
                         doc: Doc) -> List[Extraction]:

        mf = MatcherFactory(self.vocab)

        index_matcher: Matcher = mf.get_matcher(kind_of_index_to_find)
        np_matcher = mf.get_matcher(MatchKind.np)

        output: List[Extraction] = []

        iv_indexes: List[int] = self._get_matching_indexes_in_doc(doc,
                                                                  index_matcher)  # noqa: E501
        nps = np_matcher(doc)
        for match_id, start, end in nps:
            span = Span(doc, start, end, label=match_id)
            start_within_K: bool = self._within_K(start, iv_indexes)
            end_within_K: bool = self._within_K(end, iv_indexes)
            start_character_offset: int = doc[start].idx
            if start_within_K or end_within_K:
                extraction = Extraction(kind_of_extraction=kind_of_index_to_find.value,  # noqa: E501
                                        character_offset=start_character_offset,  # noqa: E501
                                        document_filename=doc._.filename,
                                        text_of_extraction=str(span))
                output.append(extraction)

        return output
