# %%

from typing import List

import numpy as np
from numpy import ndarray
from sklearn.neighbors import KDTree
from spacy import Vocab

from src.logger import get_logger
from src.pipelines.pipeline_config import PipelineConfig
from src.semantic_similarity.extractions_file_reader import (  # noqa: E501
    ExtractionsFileReader,
)
from src.semantic_similarity.kdt_provider import KDT_provider


class SimilarityFinder(object):

    def __init__(
        self,
        vocab: Vocab,
        provider: KDT_provider,
    ):
        self.logger = get_logger()
        self.vocab = vocab

        tree, extracted_variable_names, extracted_variable_vectors = provider.get_tree_and_variable_names()  # noqa: E501
        self.tree: KDTree = tree
        self.extracted_variable_names: List[str] = extracted_variable_names
        self.extracted_variable_vectors: List[ndarray] = extracted_variable_vectors  # noqa: E501

    def find_similar(self, query: str = "wages", K: int = 200) -> List[dict]:

        query_vector = self._get_query_vector(query)

        distances, indexes = self.tree.query(query_vector, k=K)

        output: List[dict] = []

        # turn 2d arrays in 1d arrays
        assert distances.shape[0] == 1
        assert indexes.shape[0] == 1
        distances = distances[0]
        indexes = indexes[0]

        for index, distance in zip(indexes, distances):
            word: str = self.extracted_variable_names[index]
            # mypy won't allow typedef in unpacking 2 lines up, # noqa: E501
            distance: float = distance  # type: ignore
            output.append({"term": word, "distance": distance})

        return output

    def _average_vectors(self, vectors: List[ndarray]) -> ndarray:
        return np.mean(vectors, axis=0)

    def _get_query_vector_from_known_variables(self, query: str) -> ndarray:
        query_index = self.extracted_variable_names.index(query)
        query_vector = self.extracted_variable_vectors[query_index]
        query_vector = query_vector.reshape(1, -1)
        return query_vector

    def _get_query_vector_by_resorting_to_averaging(self,
                                                    query: str) -> ndarray:
        # spacy's vocab.get_vector returns \vec{0} if not present
        # https://github.com/explosion/spaCy/blob/master/spacy/vocab.pyx#L386
        query_vector = self._average_vectors([self.vocab.get_vector(i) for i in query.split()])  # type: ignore # noqa: E501

        logger = get_logger()
        query_vector = query_vector.reshape(1, -1)

        msg = '[*] Could not find query in known variables'
        msg = msg + ", averaging the words in query"
        logger.info(msg)
        if np.sum(query_vector) == 0:
            raise ValueError(f"[*] Semantic suggester's vocab not recogize any of the words query={query}. Is it a typo?")  # noqa: E501

        return query_vector

    def _get_query_vector(self, query: str) -> ndarray:

        if query in self.extracted_variable_names:
            return self._get_query_vector_from_known_variables(query)
        else:
            return self._get_query_vector_by_resorting_to_averaging(query)


if __name__ == "__main__":

    config = PipelineConfig(corpus="s2orc_abstracts")
    reader = ExtractionsFileReader(config)
    provider = KDT_provider(variable_reader=reader,
                            config=config)
    tree = SimilarityFinder(vocab=config.vocab, provider=provider)
    tree.find_similar("wage theft")
