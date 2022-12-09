from typing import List

from src.pipelines.pipeline_config import PipelineConfig
from src.semantic_similarity.semantic_variable import SemanticVariable


class VariableReaderInterface:
    def __init__(self, config: PipelineConfig) -> None:
        pass  # set any internal variables based on the config object

    def get_variables(self) -> List[SemanticVariable]:
        """Return a list of variables"""
        pass
