import os
from pathlib import Path
from typing import List

from spacy.matcher import Matcher

from src.extractors.matcher_factory import MatcherFactory, MatchKind
from src.extractors.rule_based_extractor import RuleBasedExtractor
from src.graph_builders.extractions_to_networkx import (  # noqa: E501
    Extractions2NetworkXConverter,
)
from src.pipelines.helpers import jsonl_2_txt
from src.pipelines.pipeline_config import PipelineConfig
from src.semantic_similarity.extractions_file_reader import (  # noqa: E501
    ExtractionsFileReader,
)
from src.semantic_similarity.kdt_provider import KDT_provider
from src.semantic_similarity.similarity_finder import SimilarityFinder
from src.semantic_similarity.similarity_index_builder import (  # noqa: E501
    SimilarityIndexBuilder,
)


class Pipeline(object):

    def __init__(self, config: PipelineConfig) -> None:
        corpus: str = config.corpus
        self.config = config

        if self.config.clear_cache:
            # clear the tmp directories
            os.system(f"rm -rf tmp/{config.corpus}")
            # also clear the data/corpus/txt folder, which stores txt files
            # if you clear the cache, remake this from the jsonl
            os.system(f"find data/{config.corpus}/txt -type f | xargs rm")

        for step in config.directories:
            os.system(f"mkdir -p data/{corpus}/{step}")

        os.system(f"mkdir -p tmp/{corpus}/splits")
        os.system(f"mkdir -p tmp/{corpus}/proc")
        os.system(f"mkdir -p tmp/indexes/{corpus}")

    def run(self) -> None:
        config = self.config

        corpus = config.corpus

        jsonl_2_txt(papers_filename=config.docs_filename,
                    text_field=config.docs_text_field,
                    id_field=config.docs_id_field,
                    corpus=config.corpus,
                    debug_mode=config.debug_mode,
                    debug_max=config.debug_max
                    )

        # process corpus with spacy
        os.system(f"./scripts/process_corpus_locally_with_spacy.sh {corpus}")

        self._run_rule_based_extractions()

        if config.use_semantic_similarities:
            # build an index of semantic similarities
            self._index_similarities()
            self._index_phrases()

        # build a graph of the extractions
        converter = Extractions2NetworkXConverter(
            config=config,
            verbose=True
        )
        converter.build_and_serialize()

        # copy file for the main.py program
        extension: str = "rulebased.extractions.jsonl.nxdigraph.json"
        os.system(f"cp data/{corpus}/graphs/{extension} src/dags/{corpus}.{extension}")  # noqa: E501

    def _index_similarities(self) -> None:
        rules_reader = ExtractionsFileReader(self.config,
                                             extractions_file_basename="rulebased.extractions.jsonl")  # noqa: E501
        phrase_reader = ExtractionsFileReader(self.config,
                                              extractions_file_basename="phrases.jsonl")  # noqa: E501
        provider = KDT_provider(variable_readers=[rules_reader, phrase_reader],
                                force_reindexing=True,
                                config=self.config)
        finder: SimilarityFinder = SimilarityFinder(vocab=self.config.vocab,
                                                    provider=provider)
        builder = SimilarityIndexBuilder(finder=finder, config=self.config)
        builder.build_index()

    def _index_phrases(self) -> None:
        factory = MatcherFactory(self.config.vocab)
        phrase_matcher: Matcher = factory.get_matcher(kind=MatchKind.np)
        phrase_extractor: RuleBasedExtractor = RuleBasedExtractor(config=config,  # noqa: E501
                                                                  matcher=phrase_matcher)  # noqa: E501
        phrase_extractor.run(path_to_output_file=config.path_to_phrases)

    def _run_rule_based_extractions(self) -> None:
        path_to_output_file: Path = config.path_to_rule_based_extractions

        factory = MatcherFactory(config.vocab)

        paths_to_rules: List[str] = ["config/rules/effect_of_x_on_y.json"]
        paths_to_rules.append("config/rules/relationship_between_x_on_y.json")
        matcher: Matcher = factory.get_matcher_from_rules(paths_to_rules)

        rule_based_extractor: RuleBasedExtractor = RuleBasedExtractor(config=config,  # noqa: E501
                                                                      matcher=matcher)  # noqa: E501

        rule_based_extractor.run(path_to_output_file=path_to_output_file)  # noqa: E501


if __name__ == "__main__":
    corpus: str = "nber_abstracts"
    docs_text_field = "abstract"
    docs_id_field = "nber_paper_id"
    config: PipelineConfig = PipelineConfig(corpus=corpus,
                                            debug_mode=False,
                                            clear_cache=True,
                                            use_semantic_similarities=False,
                                            debug_max=5,
                                            docs_id_field=docs_id_field,
                                            docs_text_field=docs_text_field)
    pipeline: Pipeline = Pipeline(config)
    pipeline.run()
