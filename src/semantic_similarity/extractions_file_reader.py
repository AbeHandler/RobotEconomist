import json
from pathlib import Path
from typing import List

import numpy as np
from numpy import ndarray
from tqdm import tqdm as tqdm

from src.logger import get_logger
from src.pipelines.pipeline_config import PipelineConfig
from src.semantic_similarity.semantic_variable import SemanticVariable
from src.semantic_similarity.variable_reader_interface import (  # noqa: E501
    VariableReaderInterface,
)


class ExtractionsFileReader(VariableReaderInterface):
    '''
    Read a list of extracted variable names and vectors

    Basically yhe
    '''
    def __init__(self,
                 config: PipelineConfig,
                 extractions_file_basename: str = "rulebased.extractions.jsonl"
                 ) -> None:

        corpus: str = config.corpus
        data_dir: str = config.data_dir

        self.path_to_extractions = Path(data_dir,
                                        config.corpus,
                                        config.extractions_dir,
                                        extractions_file_basename)

        self.index_directory = Path(config.index_directory)
        self.corpus = corpus

        self.logger = get_logger()

        self._validate_initalization()

    def get_variables(self) -> List[SemanticVariable]:
        out: List[SemanticVariable] = []
        # you could use a comparison method w/ a set but not worth it
        extracted_variable_names: List[str] = []

        with open(self.path_to_extractions, "r") as inf:
            msg: str = f"[*] Reading {self.path_to_extractions.as_posix()}"
            for line_number, line in tqdm(enumerate(inf), desc=msg):
                line = json.loads(line)
                variable_x = line["variable_x"]
                variable_y = line["variable_y"]
                vector_x: ndarray = np.asarray(line["vector_x"])
                vector_y: ndarray = np.asarray(line["vector_y"])

                if variable_x not in extracted_variable_names:
                    out.append(SemanticVariable(name=variable_x,
                                                vector=vector_x)
                               )
                    extracted_variable_names.append(variable_x)

                if variable_y not in extracted_variable_names:
                    out.append(SemanticVariable(name=variable_y,
                                                vector=vector_y)
                               )
                    extracted_variable_names.append(variable_y)

        return out

    def _validate_initalization(self) -> None:
        if not self.path_to_extractions.exists():
            msg: str = f"[*] {self.path_to_extractions.as_posix()} not found"
            raise FileNotFoundError(msg)


if __name__ == "__main__":
    config: PipelineConfig = PipelineConfig(corpus="s2orc_abstracts")
    reader = ExtractionsFileReader(config=config)
    reader.get_variables()
