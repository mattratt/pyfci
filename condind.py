# Notes:
#
# Possible "universal test":
# https://arxiv.org/pdf/1804.02747.pdf

import math
import logging
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats


logg = logging.getLogger(__name__)


def partial_corr(xvals, yvals, condvals):
    xvals = np.array(xvals)
    yvals = np.array(yvals)
    condvals = np.array(condvals)

    num_conds = condvals.shape[1]
    if num_conds == 0:
        r, _ = stats.pearsonr(xvals, yvals)
    else:
        zvals = condvals[:, 0]
        condvals_rest = condvals[:, 1:]
        rxy_rest = partial_corr(xvals, yvals, condvals_rest)
        rxz_rest = partial_corr(xvals, zvals, condvals_rest)
        rzy_rest = partial_corr(zvals, yvals, condvals_rest)
        num = rxy_rest - (rxz_rest*rzy_rest)
        den = math.pow((1.0-rxz_rest**2)*(1.0-rzy_rest**2), 0.5)
        r = num / den
    return r


def partial_corr_pval(r, n):
    # if we want the pval, we're going to need the zscore instead of r
    # see: https://tinyurl.com/ycdbexzj
    z = r2zscore(r, n)
    p = zscore_pval(z)
    return p


def r2zscore(r, n):
    fisher = 0.5*math.log((1.0+r)/(1.0-r))
    z = math.pow(n - 3, 0.5) * fisher
    return z


def zscore_pval(z):
    return 2.0*(1.0 - stats.norm.cdf(abs(z)))  #zzz should this be abs(z)?!


# class Contingency:
#     def __init__(self, row_vals, col_vals):
#         self.n = 0
#         self.counts = defaultdict(int)  # (row, col) -> count
#         self.marginals_row = defaultdict(int)
#         self.marginals_col = defaultdict(int)
#         for val_tup in zip(row_vals, col_vals):
#             self.n += 1
#             self.counts[val_tup] += 1
#             self.marginals_row[val_tup[0]] += 1
#             self.marginals_col[val_tup[1]] += 1
#
#     def chisq(self):
#         ret = 0.0
#         for valRow, marginalRow in self.marginals_row.items():
#             for valCol, marginalCol in self.marginals_col.items():
#                 valTup = (valRow, valCol)
#                 observed = self.counts.get(valTup, 0)
#                 expected = marginalRow * marginalCol / float(self.n)
#                 ret += (observed - expected) ** 2 / expected
#         return ret
#
#     def gstat(self):
#         ret = 0.0
#         for valRow, marginalRow in self.marginals_row.items():
#             for valCol, marginalCol in self.marginals_col.items():
#                 valTup = (valRow, valCol)
#                 observed = self.counts.get(valTup, 0)
#                 if (observed > 0):
#                     expected = marginalRow * marginalCol / float(self.n)
#                     ret += 2 * observed * math.log(observed / expected)
#         return ret
#
#     def dof(self):
#         return (len(self.marginals_row) - 1) * (len(self.marginals_col) - 1)
#
#     def levels(self):
#         return (len(self.marginals_row), len(self.marginals_col))



def chisq_3d(xvals, yvals, condvals):
    strat__xvals = {}
    strat__yvals = {}

    for x, y, strat in zip(xvals, yvals, condvals):
        strat__xvals.setdefault(strat, []).append(x)
        strat__yvals.setdefault(strat, []).append(y)

    dofs = []
    chisqs = []
    max_levels_row = 1
    max_levels_col = 1

    logg.debug("chisq3d partitioned %d tuples into %d strats\n", len(xvals), len(strat__xvals))
    for strat, xlist in strat__xvals.items():
        ylist = strat__yvals[strat]

        # cont = Contingency(xlist, ylist)
        # dofs.append(cont.dof())
        # chisqs.append(cont.chisq())
        # lev_r, lev_c = cont.levels()
        # levels_row.append(lev_r)
        # levels_col.append(lev_c)
        # logg.debug("\t%s\n%s\n",  str(strat), cont.dump())

        contingency = pd.crosstab(xlist, ylist)
        chi2, p, dof, expected = stats.chi2_contingency(contingency)
        dofs.append(dof)
        chisqs.append(chi2)
        lev_r, lev_c = contingency.shape
        max_levels_row = max(max_levels_row, lev_r)
        max_levels_col = max(max_levels_col, lev_c)

    sum_chisq = sum(chisqs)

    # if all strats had a 1x1 contingency table, conclude that items
    # are conditionally independent
    # if (max(levels_row) == 1) or (max(levels_col) == 1):
    if (max_levels_row == 1) or (max_levels_col == 1):
        logg.debug("max levels row: %f, max levels col %f\n", max_levels_row, max_levels_col)
        pval = 1.0
    else:
        pval = stats.chi2.sf(sum_chisq, sum(dofs))
    return sum_chisq, pval


