import itertools
import networkx as nx


MARK_CIRCLE = -1
MARK_EMPTY = 1
MARK_ARROW = 2


class PartiallyOrientedGraph (nx.Graph):
    def __init__(self, vertices):
        super(PartiallyOrientedGraph, self).__init__()
        self.add_nodes_from(vertices)
        self.orients = {}

    def complete(self):
        self.add_edges_from([ e for e in itertools.combinations(self.nodes(), 2) ])

    def set_orient(self, a, b, mark_a, mark_b):
        self.orients[(a, b)] = (mark_a, mark_b)
        self.orients[(b, a)] = (mark_b, mark_a)

    def get_orient(self, a, b):
        return self.orients[(a, b)]







