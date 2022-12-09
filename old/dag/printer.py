from src.dag.dag import Dag
from random import random
import json
from src.config import Config
import networkx as nx  # type: ignore


class Printer(object):

    '''
    Prints the dags, like in Mellon (2021)

    This is mostly used for debugging/analysis
    '''

    def get_vertical_position(self, node: str) -> float:

        if node == "IV":
            return 1
        elif node == "U":
            return .5
        else:
            return random()

    # TODO refactor. Assumes variable names below
    def get_horizontal_position(self, node) -> float:
        if node == self.config.instrument:
            return 0
        elif node == "U":
            return 0
        elif node == self.config.outcome:
            return 1
        elif node == "X":
            return .5
        elif node == "Z":
            return .5
        else:
            return random()

    # i guess you might want to pass a color map but seems like overkill
    def make_color_map(self) -> None:
        self.color_map = []
        for node in self.dag.G.nodes:
            if node == self.config.outcome:
                self.color_map.append('purple')
            elif node == self.config.instrument:
                self.color_map.append("red")
            else:
                self.color_map.append('green')

    def __init__(self,
                 dag: Dag,
                 display_graph_on_screen: bool = False,
                 output_filename: str = None,
                 config: Config = Config()) -> None:

        assert type(display_graph_on_screen) == bool

        self.dag = dag

        self.config = config

        # networkx name for position
        self.pos = {node: (self.get_horizontal_position(node),
                           self.get_vertical_position(node))
                    for node in list(dag.G.nodes)}

        self.make_color_map()

        self.options = {"edgecolors": "tab:gray",
                        "node_size": 800, "alpha": 0.5}

        nx.draw_networkx(dag.G, self.pos,
                         node_color=self.color_map, **self.options)

        nx.draw_networkx_edge_labels(
            dag.G, self.pos, edge_labels=dag.relationships)

        # e.g. mydag.pdf
        if output_filename is not None:
            import matplotlib.pyplot as plt  # type: ignore
            plt.savefig(output_filename)
        if display_graph_on_screen:
            import matplotlib.pyplot as plt  # type: ignore
            plt.show()
