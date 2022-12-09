from random import random
from dataclasses import dataclass
import json
from re import I
from tkinter import Label
from typing import List, Set
import networkx as nx  # type: ignore
from src.dag.vertex import Vertex
from src.dag.edge import Edge



class Dag(object):

    '''
    A directed acyclic graph representing
    relationships between variables
    '''

    def __init__(self,
                 vertexes: List[Vertex],
                 edges: Set[Edge]
                 ) -> None:

        self.G = nx.DiGraph()
        self.relationships = {}
        self.vertexes = vertexes
        self.edges = edges

        for vertex in vertexes:
            self.G.add_node(vertex.vertex_id)

        for edge in edges:
            A = edge.A
            B = edge.B
            A_id, B_id = A.vertex_id, B.vertex_id
            self.G.add_edge(A_id, B_id)
            self.relationships[(A_id, B_id)] = edge.label

