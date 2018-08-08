# Notes:
#
# Possible "universal test":
# https://arxiv.org/pdf/1804.02747.pdf

import math
import logging
from collections import defaultdict
import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_categorical_dtype, is_numeric_dtype
from scipy import stats


logg = logging.getLogger(__name__)


class CondIndTester(object):
    def __init__(self, df):
        self.df = df

    def cond_ind(self, a_col_name, b_col_name, cond_col_names, alpha):
        a = self.df[a_col_name]
        b = self.df[b_col_name]
        conds = [self.df[z] for z in cond_col_names]

        if is_bool_dtype(a) and is_bool_dtype(b) and all([is_bool_dtype(z) for z in conds]):
            stat, pval = cmh(a, b, conds)

        elif (is_categorical_dtype(a) or is_bool_dtype(a)) and \
                (is_categorical_dtype(b) or is_bool_dtype(b)) and \
                all([is_categorical_dtype(z) or is_bool_dtype(z) for z in conds]):
            stat, pval = chisq_3d(a, b, conds)

        elif is_numeric_dtype(a) and \
                is_numeric_dtype(b) and \
                all([is_categorical_dtype(z) or is_bool_dtype(z) for z in conds]):
            stat, pval = blocked_pearson(a, b, conds)

        elif is_numeric_dtype(a) and \
                is_numeric_dtype(b) and \
                all([is_numeric_dtype(z) for z in conds]):
            stat, pval = partial_corr_r(a, b, conds)

        else:
            stat, pval = freak out

        return pval < alpha


class CondIndOracle(CondIndTester):
    zzz


def partial_corr(xvals, yvals, condvals):
    r = partial_corr_r(xvals, yvals, condvals)
    # if we want the pval, we're going to need the zscore instead of r
    # see: https://tinyurl.com/ycdbexzj
    n = len(xvals)
    z = r2zscore(r, n)
    p = zscore_pval(z)
    return r, p  #zzz should we be returning z here?


def partial_corr_r(xvals, yvals, condvals):
    xvals = np.array(xvals)
    yvals = np.array(yvals)
    condvals = np.array(condvals)

    num_conds = condvals.shape[1]
    if num_conds == 0:
        r, _ = stats.pearsonr(xvals, yvals)
    else:
        zvals = condvals[:, 0]
        condvals_rest = condvals[:, 1:]
        rxy_rest = partial_corr_r(xvals, yvals, condvals_rest)
        rxz_rest = partial_corr_r(xvals, zvals, condvals_rest)
        rzy_rest = partial_corr_r(zvals, yvals, condvals_rest)
        num = rxy_rest - (rxz_rest*rzy_rest)
        den = math.pow((1.0-rxz_rest**2)*(1.0-rzy_rest**2), 0.5)
        r = num / den
    return r


def r2zscore(r, n):
    fisher = 0.5*math.log((1.0+r)/(1.0-r))
    z = math.pow(n - 3, 0.5) * fisher
    return z


def zscore_pval(z):  #zzz need to figure out correct calc
    # return 2.0*(1.0 - stats.norm.cdf(abs(z)))
    return -2*stats.norm.cdf(-np.abs(z))


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


