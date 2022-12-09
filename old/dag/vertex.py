from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Vertex:
    variable_name: str  # e.g. "weather"

    # early on, variable type was part of a dag vertex but this is wrong
    # the thing the same var may be an instrument in one paper but a var
    # in another. e.g. mood may be an instrument in one paper and a regressor in another
    # variable_type: str  # e.g. "IV"

    papers_id: List[str]  # e.g. "johnson.jsonl"
    vertex_id: int  # I guess a better version of this would use a string, see eq

    def __hash__(self) -> int:
        return hash(str(self.vertex_id))

    def __eq__(self, other) -> bool:  # type: ignore
        '''
        Vertex ID does not matter for uniqely identifying vertexes in a dag
        we need a vertex id for compatability with networkx
        a better thing would be to use string for vertex_id #TODO
        '''
        if type(self) != type(other):
            raise TypeError(
                "You are trying to compare something that is not a Vertex to a Vertex")
        if self.variable_name == other.variable_name:
            if set(self.papers_id) == set(other.papers_id):
                return True
            else:
                return False
        else:
            return False

    def pretty_print(self) -> str:
        return "({})".format(self.variable_name)
