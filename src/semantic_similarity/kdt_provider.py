
import pickle
from asyncio.log import logger
from pathlib import Path
from typing import List, Tuple

import numpy as np
from numpy import ndarray
from sklearn.neighbors import KDTree

from src.logger import get_logger
from src.pipelines.pipeline_config import PipelineConfig
from src.semantic_similarity.extractions_file_reader import (  # noqa: E501
    ExtractionsFileReader,
)
from src.semantic_similarity.semantic_variable import SemanticVariable
from src.semantic_similarity.variable_reader_interface import (  # noqa: E501
    VariableReaderInterface,
)


class KDT_provider(object):
    '''
    Provide a KDT tree. If the tree has not been indexed already it will build
    the index. Otherwise it will load the index from disk
    '''

    def __init__(self,
                 variable_readers: List[VariableReaderInterface],
                 config: PipelineConfig,
                 force_reindexing: bool = False):

        self.variable_readers = variable_readers
        self.config = config
        self.corpus = config.corpus
        self.logger = get_logger()

        if force_reindexing:
            self._setup_index()
            self._index_tree()

        self.path_to_index: Path = self._get_path_to_indexed_file()

        if not self.path_to_index.exists():
            self._index_tree()

    def get_tree_and_variable_names(self) -> Tuple[KDTree, List[str], List[ndarray]]:  # noqa: E501
        self.path_to_index = self._get_path_to_indexed_file()  # noqa: E501
        tree, extracted_variable_names, extracted_variable_vectors = self._load_tree_and_metadata()  # noqa: E501
        return tree, extracted_variable_names, extracted_variable_vectors

    def _get_path_to_indexed_file(self) -> Path:
        index_directory: Path = Path(self.config.index_directory)
        indexed_path_to_extractions = index_directory / self.config.corpus / self.config.kdt_index_basename  # noqa: E501
        return indexed_path_to_extractions

    def _setup_index(self) -> None:
        (self.config.index_directory / Path(self.corpus)).mkdir(parents=True,
                                                         exist_ok=True)

    def _build_tree(
        self,
        leaf_size: int = 2
    ) -> Tuple[KDTree, List[str], List[ndarray]]:

        variables: List[SemanticVariable] = []  # noqa: E501
        for reader in self.variable_readers:
            variables = variables + reader.get_variables()

        extracted_variable_vectors: List[ndarray] = [o.vector for o in variables]  # noqa: E501
        extracted_variable_names: List[str] = [o.name for o in variables]  # noqa: E501
        self.logger.info(len(extracted_variable_vectors))
        M = np.vstack(extracted_variable_vectors)
        tree: KDTree = KDTree(M, leaf_size=leaf_size)
        return (tree, extracted_variable_names, extracted_variable_vectors)

    def _index_tree(self) -> None:

        path_to_index: str = self._get_path_to_indexed_file()

        with open(path_to_index, "wb") as of:
            tree, extracted_variable_names, extracted_variable_vectors = self._build_tree()  # noqa: E501
            pickle.dump([tree, extracted_variable_names, extracted_variable_vectors], of)  # noqa: E501
            message = "[*] Built index and wrote to {}".format(path_to_index)  # noqa: E501
            self.logger.info(message)

    def _load_tree_and_metadata(self) -> tuple:

        with open(self.path_to_index, "rb") as inf:
            # dump information to that file
            tree, extracted_variable_names, extracted_variable_vectors = pickle.load(inf)  # noqa: E501
            # for some reason np arrays are getting pickled as
            # lists so just convert them to arrays
            extracted_variable_vectors = [np.asarray(n) for n in extracted_variable_vectors]  # noqa: E501
            return tree, extracted_variable_names, extracted_variable_vectors


if __name__ == "__main__":
    config = PipelineConfig(corpus="s2orc_abstracts")
    reader = ExtractionsFileReader(config)
    provider = KDT_provider(variable_readers=[reader],
                            config=config)
