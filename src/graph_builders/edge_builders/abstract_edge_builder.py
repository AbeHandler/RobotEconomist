from abc import ABC, abstractmethod
from typing import List, Tuple


class AbstractEdgeBuilder(ABC):
    @abstractmethod
    def read_edges_from_file(self, **kwargs) -> List[Tuple[str, str, List[dict]]]:
        pass
