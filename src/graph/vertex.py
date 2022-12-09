from typing import NamedTuple


class Vertex(NamedTuple):
    name: str

    def __str__(self) -> str:
        return str(self.name)

    def __eq__(self, other):
        if isinstance(other, Vertex):
            return self.name == other.name
        else:
            return False
