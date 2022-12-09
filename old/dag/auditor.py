from src.dag.dag import Dag
from src.dag.vertex import Vertex
from src.dag.edge import Edge
import networkx as nx  # type: ignore


class Auditor(object):

    '''
    An auditor that finds all paths in DAG.
    If the DAG is kosher then there is one
    path from the IV to the outcome
    '''

    def __init__(self, dag: Dag) -> None:
        self.dag = dag

    def audit(self, source: Vertex, sink: Vertex, verbose: bool = False) -> list:
        out = []
        path_count = 0
        paths = nx.all_simple_paths(self.dag.G,
                                    source.vertex_id,
                                    sink.vertex_id)
        paths = list(paths)
        if verbose:
            print("- Found {} paths from IV to outcome".format(len(paths)))
        for path in paths:
            out.append(tuple(path))
            if verbose:
                self.pretty_print_path(path, path_count)
            path_count += 1
        return out

    def get_vertex(self, vertex_no: int) -> Vertex:
        return next(v for v in self.dag.vertexes if v.vertex_id == vertex_no)

    def get_edge(self, A: Vertex, B: Vertex) -> Edge:
        edge = next(o for o in self.dag.edges if o.A.vertex_id ==
                    A.vertex_id and o.B.vertex_id == B.vertex_id)
        return edge

    def pretty_print_path(self, path: list, path_count: int) -> None:
        print("\nPath number {} from IV to outcome".format(path_count))
        for vertexno, vertex in enumerate(path):
            vertex = self.get_vertex(vertex)
            if vertexno >= 0 and vertexno < (len(path) - 1):
                nextv = path[vertexno + 1]
                nextv = next(
                    o for o in self.dag.vertexes if o.vertex_id == nextv)
                edge = self.get_edge(vertex, nextv)
                b = edge.pretty_print()
                print(b)

    def is_kosher(self, source: Vertex, sink: Vertex) -> bool:
        paths = self.audit(source, sink)
        # this is too agressive if noisy tagger
        #error_msg = "Expect at minimum IV -> regressor -> outcome"
        #assert len(paths) > 0, error_msg
        return len(paths) < 2
