import json
from copy import deepcopy
from pathlib import Path
from typing import List

from tqdm import tqdm as tqdm

from src.logger import get_logger
from src.pipelines.pipeline_config import PipelineConfig
from src.semantic_similarity.extractions_file_reader import (  # noqa: E501
    ExtractionsFileReader,
)
from src.semantic_similarity.kdt_provider import KDT_provider
from src.semantic_similarity.similarity_finder import SimilarityFinder


class SimilarityIndexBuilder(object):

    def __init__(self,
                 finder: SimilarityFinder,
                 config: PipelineConfig,
                 explore_steps: int = 1,  # noqa:E501 how many steps to query neighbors of neighborsl
                 K_neighbors: int = 10):
        self.finder: SimilarityFinder = finder
        self.config: PipelineConfig = config
        # how many neighbors to extract from kdt
        self.K_neighbors: int = K_neighbors
        self.path_to_input_extractions: Path = Path(config.data_dir,
                                                    config.corpus,
                                                    config.extractions_dir,
                                                    config.extractions_basename)  # noqa: E501
        self.path_to_output_index: Path = Path(config.data_dir,
                                               config.corpus,
                                               config.similarities_dir,
                                               config.similarities_basename)
        self.logger = get_logger()

    def build_index(self) -> None:

        similarities: List[dict] = self._get_all_similarities()
        self._write_index(similarities)

    def _write_index(self, similarities: List[dict]) -> None:
        path: str = self.path_to_output_index.as_posix()
        self.logger.info("[*] wrote similarities index to {path}")
        with open(path,  "w") as of:
            for similarity in similarities:
                of.write(json.dumps(similarity) + "\n")

    def _get_all_similarities(self, explore_steps: int = 1) -> List[dict]:

        output: List[dict] = []
        with open(self.path_to_input_extractions.as_posix(), "r") as inf:
            path: str = self.path_to_input_extractions.as_posix()
            msg: str = f"[*] querying similarities for index from {path}"
            total: int = sum(1 for i in open(path))
            for i in tqdm(inf, desc=msg, total=total):  # noqa: E501
                i = json.loads(i)
                x = i['variable_x']
                y = i['variable_y']
                output = output + self._get_similarities_from_query(x)
                output = output + self._get_similarities_from_query(y)

                explored = self._explore_frontier(frontier=[x],
                                                  steps_remaining=explore_steps)  # noqa: E501

                output = output + explored

        return output

    def _get_similarities_from_query(self, _query: str) -> List[dict]:
        output = []
        for j in self.finder.find_similar(_query, K=self.K_neighbors):
            j["term2"] = _query
            j["term1"] = j["term"]
            del j["term"]
            if j["distance"] != 0:
                output.append(j)
        return output

    def _explore_frontier(self,
                          frontier: List[str],
                          steps_remaining: int = 1
                          ) -> List[dict]:

        if steps_remaining < 1:
            return []
        else:
            all_: List[dict] = []
            current_frontier = deepcopy(frontier)
            for vertex_a in current_frontier:  # loop over current frontier

                #  find neighbors of A, and add to output
                neighbors: List[dict] = self._get_similarities_from_query(vertex_a)  # noqa: E501
                all_ = all_ + neighbors

                #  add them to frontier
                for neighbor in neighbors:
                    frontier.append(neighbor["term1"])

                #  remove vertex_a
                frontier.remove(vertex_a)

            # continue to explore frontier
            remaining = steps_remaining - 1
            all_ = all_ + self._explore_frontier(frontier=frontier,
                                                 steps_remaining=remaining)
            return all_


if __name__ == "__main__":

    config = PipelineConfig(corpus="ivis")

    rules_reader = ExtractionsFileReader(config,
                                         extractions_file_basename="rulebased.extractions.jsonl")  # noqa: E501
    phrase_reader = ExtractionsFileReader(config,
                                          extractions_file_basename="phrases.jsonl")  # noqa: E501
    provider = KDT_provider(variable_readers=[rules_reader, phrase_reader],
                            force_reindexing=False,
                            config=config)
    finder: SimilarityFinder = SimilarityFinder(vocab=config.vocab,
                                                provider=provider)
    builder = SimilarityIndexBuilder(finder=finder, config=config)
    builder.build_index()
