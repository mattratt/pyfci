import itertools
import collections
import networkx as nx
import graphs

# From Causation, Prediction, and Search (Chapter 6)
#
# Causal Inference Algorithm1
# A.) Form the complete undirected graph Q on the vertex set V.
# B.) If A and B are d-separated given any subset S of V, remove the edge between A and B, and record S in Sepset(A,B) and Sepset(B,A).
# C.) Let F be the graph resulting from step B). Orient each edge as o-o. For each triple of vertices A, B, C such that the pair A, B and the pair B, C are each adjacent in F but the pair A, C are not adjacent in F, orient A *-* B *-* C as A *→ B ←* C if and only if B is not in Sepset(A,C), and orient A *-* B *-* C as A *-* B *-* C if and only if B is in Sepset(A,C).
# D.) repeat
# If there is a directed path from A to B, and an edge A *-* B, orient A *-* B as A *→ B, else if B is a collider along <A,B,C> in   , B is adjacent to D, and D is in Sepset(A,C), then orient B *-* D as B ←* D,
# else if U is a definite discriminating path between A and B for M in   , and P and R are adjacent to M on U, and P - M - R is a triangle, then
# if M is in Sepset(A,B) then M is marked as a noncollider on subpath P *-* M *-* R
# else P *-* M *-* R is oriented as P *→ M ← * R. else if P *→ M *-* R then orient as P *→ M → R.2
# until no more edges can be oriented.




def find_seps(g, a, b):
    conds = set(g.nodes()) - {a, b}
    for n in range(len(conds) + 1):
        for seps in itertools.combinations(conds, n):
            if cond_indy(g, a, b, seps):
                return frozenset(seps)
    return None


def cond_indy(data, a, b, conds):
    #zzz
    return True



##################################################

vertices = ['a', 'b', 'c']  #zzz

# Form the complete undirected graph Q on the vertex set V.
# g = nx.complete_graph(len(vertices))
# nx.relabel_nodes(q, dict(zip(vertices, g.nodes())))
g = graphs.MixedGraph(vertices)
g.complete()

# If A and B are d-separated given any subset S of V, remove the edge between A and B, and record
# S in Sepset(A,B) and Sepset(B,A).
sep_set = {}  # (s, t) => { x, y, z}
for a, b in g.edges():
    seps = find_seps(g, a, b)
    if seps is not None:
        g.remove_edge(a, b)
        sep_set[frozenset([a, b])] = seps

# Orient each edge as o-o.
for a, b in g.edges():
    g.set_orient(a, b, graphs.Mark.CIRCLE, graphs.Mark.CIRCLE)

# For each triple of vertices A, B, C such that the pair A, B and the pair B, C are each adjacent
# in F but the pair A, C are not adjacent in F, orient A *-* B *-* C as A *-> B <-* C if and only
# if B is not in Sepset(A,C), and orient A *-* B *-* C as A *-* B *-* C if and only if B is in
# Sepset(A,C).
for a, b, c in g.get_unshields():
    if b not in sep_set[frozenset([a, c])]:
        g.set_orient(a, b, None, graphs.Mark.ARROW)
        g.set_orient(b, c, graphs.Mark.ARROW, None)
    else:
        g.set_noncollider(a, b, c)

# repeat
#     If there is a directed path from A to B, and an edge A *-* B,
#         orient A *-* B as A *-> B,
#     else if B is a collider along <A,B,C> in, B is adjacent to D, and D is in Sepset(A,C), then
#         orient B *-* D as B <-* D,
#     else if U is a definite discriminating path between A and B for M in PI, and P and R are
#      adjacent to M on U, and P - M - R is a triangle, then
#         if M is in Sepset(A,B) then
#             M is marked as a noncollider on subpath P *-* M *-* R
#         else P *-* M *-* R is oriented as P *-> M <- * R.
#     else if P *-> M *-* R then orient as P *-> M -> R.2
# until no more edges can be oriented.
updated = True
while updated:
    updated = False

    for a, b in g.edges():
        if g.has_directed_path(a, b): # and g.has_edge(a, b):
            g.set_orient(a, b, None, graphs.Mark.ARROW)
            updated = True
            continue #zzz while loop

    for a, b, c in g.get_colliders():
        for d in sep_set[frozenset([a, c])].intersection(set(g.neighbors(b))):
            g.set_orient(b, d, graphs.Mark.ARROW, None)
            updated = True
            continue #zzz while loop

    triangles = g.get_triangles()
    for a, b in itertools.combinations(g.nodes(), 2):
        for u, m in g.get_discriminating_paths(a, b):  #todo: prob should just grab first one we can
            m_idx = u.index(m)
            p = u[m - 1]
            r = u[m + 1]
            if (p, m, r) in triangles:
                if m in sep_set[frozenset([a, b])]:
                    g.set_noncollider(p, m, r)
                    updated = True
                    continue #zzz while loop
                else:
                    g.set_orient(p, m, None, graphs.Mark.ARROW)
                    g.set_orient(m, r, graphs.Mark.ARROW, None)
                    updated = True
                    continue #zzz while loop

    for p, m, r in g.get_noncolliders():
        if g.get_orient(p, m)[1] == graphs.Mark.ARROW:
            g.set_orient(m, r, graphs.Mark.EMPTY, graphs.Mark.ARROW)
        elif g.get_orient(m, r)[0] == graphs.Mark.ARROW:
            g.set_orient(p, m, graphs.Mark.ARROW, graphs.Mark.EMPTY)





