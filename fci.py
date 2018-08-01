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
    return skel, seps, unshields


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


