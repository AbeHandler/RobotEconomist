from dataclasses import dataclass

from numpy import ndarray


@dataclass
class SemanticVariable:
    """
    A semantic variable

    For instance "pensions" should be nearby to "income" in vector space
    """
    name: str
    vector: ndarray
