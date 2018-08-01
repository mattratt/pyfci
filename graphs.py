import itertools
import networkx as nx
from enum import Enum


Mark = Enum('Mark', 'CIRCLE EMPTY ARROW')


class MixedGraph (nx.Graph):
    def __init__(self, vertices, edges=None):
        super(MixedGraph, self).__init__()
        self.orients = {}
        self.add_nodes_from(vertices)
        if edges:
            for a, b in edges:
                self.add_edge(a, b)
                self.set_orient(a, b, Mark.CIRCLE, Mark.CIRCLE)

    # def complete(self):
    #     self.add_edges_from([ e for e in itertools.combinations(self.nodes(), 2) ])

    def add_edge(self, u, v, attr_dict=None, **attr):
        super(MixedGraph, self).add_edge(u, v, attr_dict, **attr)
        self.set_orient(u, v, Mark.CIRCLE, Mark.CIRCLE)

    def set_orient(self, a, b, mark_a, mark_b):
        mark_a_old, mark_b_old = self.get_orient(a, b)
        if mark_a is None:
            mark_a = mark_a_old
        if mark_b is None:
            mark_b = mark_b_old
        self.orients[(a, b)] = (mark_a, mark_b)
        self.orients[(b, a)] = (mark_b, mark_a)

    def get_orient(self, a, b):
        if not self.has_edge(a, b):
            raise Exception("can't get orient for non-existent edges {} - {}".format(a, b))
        elif (a, b) in self.orients:
            return self.orients[(a, b)]
        else:
            return (None, None)

    def get_colliders(self):
        rets = []
        for b in self.nodes():
            inbounds = [ s for s in self.neighbors(b) if self.get_orient(s, b)[1] == Mark.ARROW ]
            for a, c in itertools.combinations(inbounds, 2):
                rets.append((a, b, c))
        return rets

    def get_vees(self):
        rets = []
        for a, b, c in itertools.combinations(self.nodes(), 3):
            if self.has_edge(a, b) and self.has_edge(b, c) and (not self.has_edge(a, c)):
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

    # def get_discriminating_paths(self, a, b):
    #     return stuff
    #
    # def is_directed_path(self, u):
    #     for i in range(len(u) - 1):
    #         mark self.get_orient(u[i], u[i + 1])

    # these methods return the first qualifying thing they find

    # def find_directed_path(self, a, b):
    #     for u in nx.all_simple_paths(self, a, b):
    #         for i in range(len(u) - 1):
    #             if self.get_orient(u[i], u[i+1])


class PartiallyOrientedGraph (MixedGraph):
    def __init__(self, vertices):
        super(PartiallyOrientedGraph, self).__init__(vertices)
        self.noncolliders = set()

    def set_noncollider(self, a, b, c):
        self.noncolliders.add((a, b, c))

    def get_noncolliders(self):
        return self.noncolliders





