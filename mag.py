import sys
import logging
import json
import itertools
import networkx as nx
from asciinet import graph_to_ascii
import graphs


def get_log(nm):
    lg = logging.getLogger(nm)
    lg.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    ch.setFormatter(formatter)
    lg.addHandler(ch)
    return lg
log = get_log(__name__)


# Causation, Prediction, and Search p302
# DEFINITION 12.1.2: MAG Tau represents DAG G(O,S.L) if and only if:
# 1. If A and B are in O, there is an edge between A and B in Tau if and
#    only if for any subset W subset O\{A,B}, A and B are d-connected given
#    W union S in G(O,S, L).
# 2. There is an edge A -> B in Tau if and only if A is an ancestor of B
#    but not of S in G(O,S, L).
# 3. There is an edge A <-* B in Tau if and only if A is not an ancestor
#    of B or S in G(O,S, L).
# 4. There is an edge A o-* B in Tau if and only if A is an ancestor of
#    S in G(O,S,L). (Note that "o" has a different meaning in PAGS.)

# def findAllPathsSingle(gOrig, source, dest=None, excludes=[]):
#     """Get all paths from a single point of origin."""
#     if (excludes):
#         g = gOrig.copy()
#         for ex in excludes:
#             g.remove_node(ex)
#     else:
#         g = gOrig
#     pathsAll = []
#     path0 = [source]
#     pathsCurrent = [path0]
#     for radius in range(1, len(g)):
#         pathsExtended = extendPaths(g, pathsCurrent)
#         if (pathsExtended):
#             pathsAll.extend(pathsExtended)
#             pathsCurrent = pathsExtended
#         else:
#             break
#     if (dest is None):
#         return pathsAll
#     else:
#         return [path for path in pathsAll if (path[-1] == dest)]
#
#
# def find_all_paths(gOrig, excludes=None):
#     """Exhaustively identify all paths from every node to every node
#     within an undirected graph and return as a list.
#     """
#     g = gOrig.copy()
#     if excludes:
#         for ex in excludes:
#             g.remove_node(ex)
#     nodes = g.nodes()
#     paths_all = []
#     for source in nodes:
#         path0 = [source]
#         paths_current = [path0]
#         for radius in range(1, len(nodes)):
#             paths_extended = extend_paths(g, paths_current)
#             paths_all.extend(paths_extended)
#             paths_current = paths_extended
#     return paths_all
#
#
# def extend_paths(g, paths):
#     """Helper method for find_all_paths()"""
#     rets = []
#     for path in paths:
#         extendeds = extend_path(g, path)
#         rets += extendeds
#     return rets
#
#
# def extend_path(g, path):
#     """Helper helper method for extend_paths(), find_all_paths()"""
#     rets = []
#     used = set(path)
#     for next in g.neighbors(path[-1]):
#         if next not in used:
#             rets.append(path + [next])
#     return rets

def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1))


def cond_indy(g, x, y, conds=None):
    """Check the conditional independence of a given pair of variables."""
    if conds is None:
        conds = set()
    for path in nx.all_simple_paths(g.to_undirected(), x, y, cutoff=None):
        if d_conn(g, path, conds):
            return False
    return True


def d_conn(g, path, conds):
    """Check whether the path d-connects start and end nodes."""
    for idx in range(len(path) - 2):
        p1 = path[idx]
        p2 = path[idx + 1]
        p3 = path[idx + 2]
        if g.has_edge(p1, p2) and g.has_edge(p3, p2):  # p1 -> p2 <- p3
            if p2 not in conds:
                if not len(set(nx.dfs_successors(g, p2)).intersection(conds)) > 0:
                    return False
        else:
            if p2 in conds:
                return False
    return True


# checks to see if a is an ancestor of ANY of the bees
def is_ancestor(g, a, bees):
    descends = nx.descendants(g, a)
    for b in bees:
        if b in descends:
            return True
    return False


def get_edges_both_ways(g):
    for s, t in g.edges():
        yield (s, t)
        yield (t, s)


def mag_from_dag(dag, observed, selected, latent):
    mag = graphs.MixedGraph(dag.nodes())

    # Causation, Prediction, and Search p302
    # DEFINITION 12.1.2: MAG Tau represents DAG G(O,S.L) if and only if:
    # 1. If A and B are in O, there is an edge between A and B in Tau if and
    #    only if for any subset W subset O\{A,B}, A and B are d-connected given
    #    W union S in G(O,S, L).
    for a, b in itertools.combinations(observed, 2):
        print "checking for edge ({}, {})".format(a, b)
        has_edge = True
        for w in powerset(observed - {a, b}):
            if cond_indy(dag, a, b, set(w).union(selected)):
                print "1. {} _|_ {} | {}".format(a, b, set(w).union(selected))
                has_edge = False
                break
        if has_edge:
            mag.add_edge(a, b)

    # 2. There is an edge A -> B in Tau if and only if A is an ancestor of B
    #    but not of S in G(O,S, L).
    # for a, b in itertools.combinations(mag.nodes(), 2):  #zzz should we only check edges created in 1?

    for a, b in get_edges_both_ways(mag):
        if is_ancestor(dag, a, [b]) and not is_ancestor(dag, a, selected):
            # mag.add_edge(a, b)  #zzz necessary?
            print "2. orienting {} ---> {}".format(a, b)
            mag.set_orient(a, b, graphs.Mark.EMPTY, graphs.Mark.ARROW)

    # 3. There is an edge A <-* B in Tau if and only if A is not an ancestor
    #    of B or S in G(O,S, L).
    # for a, b in itertools.combinations(mag.nodes(), 2):  #zzz should we only check edges created in 1?
    for a, b in get_edges_both_ways(mag):
        if not (is_ancestor(dag, a, [b]) or is_ancestor(dag, a, selected)):
            # mag.add_edge(a, b)  #zzz necessary?
            print "3. orienting {} <--* {}".format(a, b)
            mag.set_orient(a, b, graphs.Mark.ARROW, None)

    # 4. There is an edge A o-* B in Tau if and only if A is an ancestor of S
    # in G(O,S,L). (Note that "o" has a different meaning in PAGS.)
    # for a, b in itertools.combinations(mag.nodes(), 2):  # zzz should we only check edges created in 1?

    # for a, b in mag.edges():
    for a, b in get_edges_both_ways(mag):
        if is_ancestor(dag, a, selected):
            # mag.add_edge(a, b)
            print "4. orienting {} o--* {}".format(a, b)
            mag.set_orient(a, b, graphs.Mark.CIRCLE, None)

    return mag


def dag_from_json(json_edges):
    dag = nx.DiGraph()
    edges = json.loads(json_edges)
    dag.add_edges_from(edges)
    return dag


##########################

if __name__ == '__main__':

    args = json.loads(sys.argv[1])

    edges = args['edges']

    dag = nx.DiGraph()
    dag.add_edges_from(edges)
    print graph_to_ascii(dag)

    selects = set(args['selects'])
    latents = set(args['latents'])
    observed = set(dag.nodes()) - selects - latents
    mag = mag_from_dag(dag, observed, selects, latents)
    print graph_to_ascii(mag)
