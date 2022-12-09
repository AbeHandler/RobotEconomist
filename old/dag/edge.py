from dataclasses import dataclass
from src.dag.vertex import Vertex


@dataclass(frozen=True)
class Edge:
    A: Vertex  # e.g. "weather, IV, johnson.jsonl"
    B: Vertex  # e.g. "weather, X, johnson.jsonl"
    label: str = "affects"  # e.g. "affects" or "instruments"

    def __hash__(self) -> int:
        return hash(str(self.A.vertex_id) + str(self.B.vertex_id))

    def __eq__(self, __o: object) -> bool:
        if type(self) != type(__o):
            return False
        if self.A == __o.A:  # type: ignore
            if self.B == __o.B:  # type: ignore
                return True
        return False

    def pretty_print(self) -> str:
        return "({}-{}->{})".format(self.A.variable_name, self.label, self.B.variable_name)
