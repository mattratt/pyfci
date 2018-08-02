import itertools
import graphs



MAX_ORDER = 10


# Algorithm 4.1
def find_skeleton(nodes, conds=None):
    if conds is None:
        conds = set()
    skel = graphs.MixedGraph.complete(nodes)
    seps = {}  # (a, b) => (x, y, z)

    for order in range(MAX_ORDER):
        for i, j in skel.edges_both():
            adjs = set(skel.neighbors(i))
            if j not in adjs:
                continue  #  must have been rendered non-adj in previous (t, s) iter
            adjs.remove(j)
            if len(adjs) >= order:
                for y in itertools.combinations(adjs, order):
                    if cond_indy(i, j, set(y).union(conds)):
                        skel.remove_edge(i, j)
                        seps[(i, j)] = seps[(j, i)] = y
                        break

    unshields = skel.get_unshields()
    # unshield_trips_blank = { (a, c) for a, b, c in unshield_trips }  # do we need this? line 19
    return skel, seps, unshields  #zzz do we really need to pass around unshields?


#zzz TODO
def cond_indy(x, y, z):
    return True


# Algorithm 4.2
def orient_vees(skel, seps, unshields):
    for i, j, k in unshields:
        if j not in seps[(i, k)]:
            skel.set_orient(i, j, None, graphs.Mark.ARROW)
            skel.set_orient(j, k, graphs.Mark.ARROW, None)
    return skel, seps


# Algorithm 4.3
def final_skeleton(skel, seps, conds=None):
    if conds is None:
        conds = set()
    for i in skel.nodes():
        for j in skel.neighbors(i):
            for order in range(MAX_ORDER):
                pds = poss_dsep(skel, i)
                pds.remove(j)
                for y in itertools.combinations(pds, order):
                    if cond_indy(i, j, set(y).union(conds)):
                        skel.remove_edge(i, j)
                        seps[(i, j)] = seps[(j, i)] = y
                        break

    for s, t in skel.edges():
        skel.set_orient(s, t, graphs.Mark.CIRCLE, graphs.Mark.CIRCLE)
    unshields = skel.get_unshields()
    return skel, seps, unshields


#zzz TODO
def poss_dsep(g, x):
    return []


def run_fci(nodes, conds=None):

    skel, seps, unshields = find_skeleton(nodes, conds)

    skel, seps = orient_vees(skel, seps, unshields)

    skel, seps, unshields = final_skeleton(skel, seps, conds)

    skel, seps = orient_vees(skel, seps, unshields)

    g = orient_edges(skel)

    return g, seps


#zzz TODO
def orient_edges(skel):
    return skel


def orient_r1(g):
    count = 0
    for alpha, beta, gamma in g.get_unshields_both():
        if (g.get_orient(alpha, beta)[1] == graphs.Mark.ARROW) and \
                (g.get_orient(beta, gamma)[0] == graphs.Mark.CIRCLE):
            g.set_orient(beta, gamma, graphs.Mark.EMPTY, graphs.Mark.ARROW)
            count += 1
    return count


def orient_r2(g):
    for tri in g.get_triangles():
        for alpha, beta, gamma in itertools.permutations(tri, 3):
            if (g.get_orient(alpha, beta) == (graphs.Mark.EMPTY, graphs.Mark.ARROW)) and \
                    (g.get_orient(beta, gamma)[1] == graphs.Mark.ARROW)


def match_edge_triple(g, alpha, beta, gamma, mark_0, mark_1, mark_2, mark_3):
    if not match_edge_pair(g, alpha, beta, mark_0, mark_1):
        return False
    if not match_edge_pair(g, beta, gamma, mark_2, mark_3):
        return False
    return True


def match_edge_pair(g, alpha, beta, mark_0, mark_1):
    mark_alpha, mark_beta = g.get_orient(alpha, beta)
    if (mark_0 is not None) and (mark_alpha != mark_0):
        return False
    if (mark_1 is not None) and (mark_beta != mark_1):
        return False
    return True










