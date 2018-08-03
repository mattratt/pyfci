import itertools
import graphs
from graphs import Mark


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

    g = orient_edges(skel, seps)

    return g, seps


def orient_edges(skel, sepsets):
    changes = 1
    while changes > 0:
        changes = 0
        changes += orient_r1(skel)
        changes += orient_r2(skel)
        changes += orient_r3(skel)
        changes += orient_r4(skel, sepsets)
    return skel


# Taken from Zhang, "On the completeness of orientation rules for
# causal discovery in the presence of latent confounders and selection
# bias" (2008)
# https://doi.org/10.1016/j.artint.2008.08.001

def orient_r1(g):
    count = 0
    for alpha, beta, gamma in g.get_unshields_both():
        if match_edge_unshield(g, alpha, None, Mark.ARROW, beta, Mark.CIRCLE, None, gamma):
            g.set_orient(beta, gamma, graphs.Mark.TAIL, graphs.Mark.ARROW)
            count += 1
    return count


def orient_r2(g):
    count = 0
    for tri in g.get_triangles():
        for alpha, beta, gamma in itertools.permutations(tri, 3):
            if match_edges_tri(g, alpha, Mark.TAIL, Mark.ARROW, beta,
                               None, Mark.ARROW, gamma, None, Mark.CIRCLE) or \
                    match_edges_tri(g, alpha, None, Mark.ARROW, beta,
                                    Mark.TAIL, Mark.ARROW, gamma, None, Mark.CIRCLE):
                g.set_orient(alpha, gamma, None, Mark.ARROW)
                count += 1
    return count


def orient_r3(g):
    count = 0
    unshields = g.get_unshields_both()
    for alpha, beta, gamma in unshields:
        for alpha2, delta, gamma2 in unshields:
            if (alpha == alpha2) and (gamma == gamma2) and (beta != delta):
                if match_edge_unshield(g, alpha, None, Mark.ARROW, beta, Mark.ARROW, None, gamma) and \
                        match_edge_unshield(g, alpha, Mark.CIRCLE, delta, Mark.CIRCLE, None, gamma) and \
                        match_edge(g, delta, None, Mark.CIRCLE, beta):
                    g.set_orient(delta, beta, None, Mark.ARROW)
                    count += 1
    return count


#zzz Todo: need to think about the effect of previous iterations on
# discriminating paths --- could an application of this rule create
# new paths for later iterations?  To be on the safe side, we exit
# after one change is made (which will greatly increase the number
# of simplepath searches.
#
# Currently thinking that this is too conservative and should change
def orient_r4(g, sepsets):
    for path in g.all_simple_paths(min_len=4):
        if g.is_discriminating(path):
            delta = path[0]
            alpha = path[-3]
            beta = path[-2]
            gamma = path[-1]
            if match_edge(g, beta, Mark.CIRCLE, None, gamma):
                if beta in sepsets[(delta, gamma)]:
                    g.set_orient(beta, gamma, Mark.TAIL, Mark.ARROW)
                else:
                    g.set_orient(alpha, beta, Mark.ARROW, Mark.ARROW)
                    g.set_orient(beta, gamma, Mark.ARROW, Mark.ARROW)
                return 1  # unlike other rules, a call to orient_r4() makes at most one change
    return 0


def match_edge(g, alpha, mark_ab0, mark_ab1, beta):
    mark_alpha, mark_beta = g.get_orient(alpha, beta)
    if (mark_ab0 is not None) and (mark_alpha != mark_ab0):
        return False
    if (mark_ab1 is not None) and (mark_beta != mark_ab1):
        return False
    return True


def match_edge_unshield(g, alpha, mark_ab0, mark_ab1, beta, mark_bg0, mark_bg1, gamma):
    return match_edge(g, alpha, mark_ab0, mark_ab1, beta) and \
           match_edge(g, beta, mark_bg0, mark_bg1, gamma)


def match_edges_tri(g, alpha, mark_ab0, mark_ab1, beta, mark_bg0, mark_bg1, gamma, mark_ag0, mark_ag1):
    return match_edge(g, alpha, mark_ab0, mark_ab1, beta) and \
           match_edge(g, beta, mark_bg0, mark_bg1, gamma) and \
           match_edge(g, alpha, mark_ag0, mark_ag1, gamma)













