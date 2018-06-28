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
        self.noncolliders = set()

    def complete(self):
        self.add_edges_from([ e for e in itertools.combinations(self.nodes(), 2) ])

    def set_orient(self, a, b, mark_a, mark_b):
        mark_a_old, mark_b_old = self.get_orient(a, b)
        if mark_a is None:
            mark_a = mark_a_old
        if mark_b is None:
            mark_b = mark_b_old
        self.orients[(a, b)] = (mark_a, mark_b)
        self.orients[(b, a)] = (mark_b, mark_a)

    def get_orient(self, a, b):
        return self.orients[(a, b)]

    def set_noncollider(self, a, b, c):
        self.noncolliders.add((a, b, c))

    def get_noncolliders(self):
        return self.noncolliders

    def get_colliders(self):
        rets = []
        for b in self.nodes():
            inbounds = [ s for s in self.neighbors(b) if self.get_orient(s, b)[1] == MARK_ARROW ]
            for a, c in itertools.combinations(inbounds, 2):
                rets.append((a, b, c))
        return rets

    def get_triangles(self):
        triangles = set()
        for b in self.nodes():
            for a, c in itertools.combinations(b.neighbors, 2):
                if self.has_edge(a, c):
                    triangles.add(frozenset([a, b, c]))
        # return [ tuple(sorted(t)) for t in triangles ]
        return triangles

    def get_discriminating_paths(self, a, b):
        return stuff