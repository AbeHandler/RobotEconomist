# %%
import json
import os
import pickle
from pathlib import Path
from typing import List

import numpy as np
import spacy
from sklearn.neighbors import KDTree
from spacy import Vocab
from tqdm import tqdm as tqdm

from scripts.interactive_rule_based_matching_for_msu_annotation import average_vectors
from src.logger import get_logger


class SemanticSuggester(object):

    def __init__(
        self,
        extractions_path: str = "data/interim/nber.rulebased.extractions.jsonl",  # noqa: E501
        force_reindexing: bool = False,  # if True, force reindexing step
        index_directory: str = "tmp/indexes",
        vocab: Vocab = None
    ):

        self.vocab = vocab
        self.extractions_path = extractions_path
        Path(index_directory).mkdir(parents=True, exist_ok=True)
        self.index_directory = index_directory
        self.logger = get_logger()
        self.path_to_index = self.get_path_to_indexed_file(extractions_path)  # noqa: E501
        if not os.path.exists(self.path_to_index) or force_reindexing:
            self._build_index()

        tree, extracted_variable_names, extracted_variable_vectors, M = self._load_index()  # noqa: E501
        self.tree = tree
        self.extracted_variable_names = extracted_variable_names
        self.extracted_variable_vectors = extracted_variable_vectors
        self.M = M

    def _build_tree(
        self,
        leaf_size: int = 2
    ) -> tuple:
        extracted_variable_names = []
        extracted_variable_vectors = []
        with open(self.extractions_path, "r") as inf:
            for line_number, line in tqdm(enumerate(inf)):
                line = json.loads(line)
                variable_x = line["variable_x"]
                variable_y = line["variable_y"]
                vector_x = line["vector_x"]
                vector_y = line["vector_y"]

                if variable_x not in extracted_variable_names:
                    extracted_variable_names.append(variable_x)
                    extracted_variable_vectors.append(vector_x)

                if variable_y not in extracted_variable_names:
                    extracted_variable_names.append(variable_y)
                    extracted_variable_vectors.append(vector_y)

        M = np.vstack(extracted_variable_vectors)
        tree = KDTree(M, leaf_size=leaf_size)
        return (tree, extracted_variable_names, extracted_variable_vectors, M)

    def get_path_to_indexed_file(self, extractions_path: str) -> str:

        basename = os.path.basename(extractions_path)
        indexed_extractions_path = os.path.join(self.index_directory, basename)
        return indexed_extractions_path

    def _build_index(self) -> None:

        with open(self.path_to_index, "wb") as of:
            tree, extracted_variable_names, extracted_variable_vectors, M = self._build_tree()  # noqa: E501
            pickle.dump([tree, extracted_variable_names, extracted_variable_vectors, M], of)  # noqa: E501
            message = "[*] Built index and wrote to {}".format(self.path_to_index)  # noqa: E501
            self.logger.info(message)

    def _load_index(self) -> tuple:

        with open(self.path_to_index, "rb") as inf:
            # dump information to that file
            tree, extracted_variable_names, extracted_variable_vectors, M = pickle.load(inf)  # noqa: E501
            return tree, extracted_variable_names, extracted_variable_vectors, M

    def query(self, query: str = "wages") -> List[str]:

        if query in self.extracted_variable_names:
            query_index = self.extracted_variable_names.index(query)
            query_vector = self.M[query_index].reshape(1, -1)
        else:
            # spacy's vocab.get_vector returns \vec{0} if not present
            # https://github.com/explosion/spaCy/blob/master/spacy/vocab.pyx#L386
            query_vector = average_vectors([self.vocab.get_vector(i) for i in query.split()])

            logger = get_logger()
            query_vector = query_vector.reshape(1, -1)
            if np.sum(query_vector) == 0:
                logger.error(f"[*] I did not recogize any of the words query={query}. Is it a typo?")
                return []
            else:
                logger.info('[*] Could not find query in known variables, looked up vectors')

        dist, indexes = self.tree.query(query_vector, k=200)

        indexes_only_dimension = indexes[0]
        for index in indexes_only_dimension:
            if query not in self.extracted_variable_names[index].lower():
                print(self.extracted_variable_names[index])

        return ["todo"]


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_md")
    tree = SemanticSuggester(vocab=nlp.vocab)
    tree.query("wage theft")
