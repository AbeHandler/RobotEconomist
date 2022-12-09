import json
from pathlib import Path
from typing import List, Tuple

import numpy as np
from numpy import ndarray
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span
from tqdm import tqdm as tqdm

from src.extractors.match_unpacker import MatchUnpacker
from src.extractors.matcher_factory import MatcherFactory
from src.logger import get_logger
from src.pipelines.helpers import read_doc_bin_from_disk, read_docs_from_disk
from src.pipelines.pipeline_config import PipelineConfig


class RuleBasedExtractor(object):
    def __init__(self, config: PipelineConfig, matcher: Matcher) -> None:
        self.matcher: Matcher = matcher
        self.config: PipelineConfig = config
        self.matchunpacker: MatchUnpacker = MatchUnpacker()

    def run(
        self,
        path_to_output_file: Path = Path(
            "data/nber/extractions/nber.rulebased.extractions.jsonl"
        ),  # noqa: E501
    ) -> None:

        # noqa: E501 this is just to redefine the path_to_output_file to have the same input type as rest of method
        path_to_output_file: str = path_to_output_file.as_posix()  # type: ignore  # noqa: E501
        path_to_docbins: str = self.config.path_to_docbins.as_posix()
        print("[*] Running on {}".format(path_to_docbins))

        try:
            Doc.set_extension("filename", default=None)
        except ValueError:
            logger = get_logger()
            logger.info("[*] Extension already exists")

        errors = 0
        logger = get_logger()
        with open(path_to_output_file, "w") as of:
            desc: str = f"[*] Running rule-based extraction on {path_to_docbins}"  # noqa:E501
            for doc in tqdm(read_docs_from_disk(self.config), desc=desc):

                matches = self.matcher(doc)
                filename = doc._.filename
                for match_id, start, end in matches:
                    # Get string representation
                    match_kind = self.config.vocab.strings[match_id]
                    match_span = doc[start:end]  # The matched match_span

                    # charcter indexes for the extracted span
                    try:
                        match_charspan_start: int = doc[start].idx
                        match_charspan_end: int = doc[end].idx + len(
                            str(doc[end])
                        )  # noqa: E501
                        match_charspan: List[int] = [
                            match_charspan_start,
                            match_charspan_end,
                        ]

                        match_serialized = self._serialize_and_unpack_match(
                            filename,  # noqa: E501
                            match_kind,  # noqa: E501
                            match_span,  # noqa: E501
                            match_charspan,
                        )  # noqa: E501
                        match_serialized["filename"] = filename
                        of.write(json.dumps(match_serialized) + "\n")
                    except IndexError:
                        # I think this is a spacy bug? In rare cases the end of
                        # the match is equal to the doc length. I am logging
                        # these cases and not worrying about them too much
                        errors += 1
                        logger.info(f"Error {filename}")
        logger.info(f"Finished with {errors} errors")

    def _average_vectors(self, vectors: List[ndarray]) -> ndarray:
        return np.mean(vectors, axis=0)

    def _span2meanvector(self, span: Span) -> ndarray:
        return self._average_vectors([o.vector for o in span])  # type: ignore

    def _serialize_and_unpack_match(
        self,
        filename: str,
        match_kind: str,
        match_span: Span,
        match_charspan: List[int],
    ) -> dict:

        variable_x, variable_y = self.matchunpacker.match2variables(match_kind, match_span)

        return {
            "vector_match_span": self._span2meanvector(match_span).tolist(),
            "method": "src.extractors.rule_based_extractor.py",
            "match_span": str(match_span),
            "filename": filename,
            "match_kind": match_kind,
            "variable_x": str(variable_x),
            "variable_y": str(variable_y),
            "variable_x_character_offset": variable_x[0].idx,
            "variable_y_character_offset": variable_y[0].idx,
            "match_charspan": match_charspan,
            "vector_x": self._span2meanvector(variable_x).tolist(),
            "vector_y": self._span2meanvector(variable_y).tolist(),
        }


if __name__ == "__main__":

    corpus: str = "nber_abstracts"
    config: PipelineConfig = PipelineConfig(corpus=corpus)

    factory = MatcherFactory(config.vocab)

    paths_to_rules: List[str] = ["config/rules/effect_of_x_on_y.json"]
    paths_to_rules.append("config/rules/relationship_between_x_on_y.json")
    matcher = factory.get_matcher_from_rules(paths_to_rules)

    extractor = RuleBasedExtractor(matcher=matcher, config=config)

    path_to_output: Path = Path(
        "data/nber_abstracts/extractions/rulebased.extractions.jsonl"
    )  # noqa: E501

    extractor.run(path_to_output_file=path_to_output)
