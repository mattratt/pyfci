import itertools
import networkx as nx
from enum import Enum


# Mark = Enum('Mark', 'CIRCLE TAIL ARROW')
class Mark(Enum):
    CIRCLE = 1
    TAIL = 2
    ARROW = 3

class MixedGraph (nx.Graph):
    def __init__(self, vertices, edges=None):
        super(MixedGraph, self).__init__()
        self.orients = {}
        self.add_nodes_from(vertices)
        if edges:
            for a, b in edges:
                self.add_edge(a, b)
                self.set_orient(a, b, Mark.CIRCLE, Mark.CIRCLE)

    @classmethod
    def complete(cls, nodes):
        return cls(nodes, itertools.combinations(nodes(), 2))

    # def complete(self):
    #     self.add_edges_from([ e for e in itertools.combinations(self.nodes(), 2) ])

    def add_edge(self, u, v, attr_dict=None, **attr):
        super(MixedGraph, self).add_edge(u, v, attr_dict, **attr)
        self.set_orient(u, v, Mark.CIRCLE, Mark.CIRCLE)

    def edges_both(self):
        for a, b in super(MixedGraph, self).edges():
            yield a, b
            yield b, a

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

    def get_connected_triples(self, both=False):
        rets = []
        for beta in self.nodes():
            for alpha, gamma in itertools.combinations(self.neighbors(node), 2):
                rets.append((alpha, beta, gamma))
                if both:
                    rets.append((gamma, beta, alpha))
        return rets

    def get_unshields(self):
        rets = []
        for a, b, c in itertools.combinations(self.nodes(), 3):
            if self.has_edge(a, b) and self.has_edge(b, c) and (not self.has_edge(a, c)):
                rets.append((a, b, c))
        return rets

    def get_unshields_both(self):
        unshields = self.get_unshields()
        unshields_rev = [(c, b, a) for a, b, c in unshields]
        return unshields + unshields_rev

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


class MaximalAncestralGraph(MixedGraph):
    def is_parent(self, a, b):
        return self.has_edge(a, b) and \
               (self.get_orient(a, b) == (Mark.TAIL, Mark.ARROW))  #zzz does this need to be empty
                                                                    # or is circle okay?

    def is_collider(self, a, b, c):
        return self.has_edge(a, b) and self.has_edge(b, c) and \
               (self.get_orient(a, b)[1] == Mark.ARROW) and \
               (self.get_orient(b, c)[0] == Mark.ARROW)

    def is_discriminating(self, path):
        #zzz can we assume paths exist?
        # for pos in range(1, len(path)):
        #     if not self.has_edge(path[pos-1], path[pos]):
        #         return False
        if len(path) < 4:
            return False
        # path is x, ..., w, v, y
        x = path[0]
        y = path[-1]
        v = path[-2]
        if self.has_edge(x, y):
            return False
        for pos in range(1, len(path)-2):
            if not (self.is_collider(path[pos-1], path[pos], path[pos+1]) and \
                    self.is_parent(path[pos], y)):
                return False
        return True

    def discriminating_paths(self):
        rets = []
        for s in self.nodes():
            for t in self.nodes():
                for path in nx.all_simple_paths(self, s, t):
                    if self.is_discriminating(path):
                        rets.append(path)
        return rets





