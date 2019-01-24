''' Functions for calculating t-table values '''

from scipy.special import nctdtridf
from scipy import stats


def t_factor(conf, degf):
    ''' Return tp(v) given confidence (0-1) and degrees of freedom.

        Parameters
        ----------
        conf: float
            Confidence value in the range (0-1).
        degf: float
            Degrees of freedom

        Returns
        -------
        tp: float
            Value of tp(v)
    '''
    return stats.t.ppf(1-(1-conf)/2, df=degf)


def confidence(tp, degf):
    ''' Get confidence value given tp and degrees of freedom. Inverse of t_factor.

        Parameters
        ----------
        tp: float
            Value of tp(v)
        degf: float
            Degrees of freedom

        Returns
        -------
        conf: float
            Confidence value in the range (0-1).
    '''
    return 1+2*(stats.t.cdf(tp, df=degf)-1)


def degf(tp, conf):
    ''' Calculate degrees of freedom given tp and confidence

        Parameters
        ----------
        tp: float
            Value of tp(v)
        conf: float
            Confidence value in the range (0-1).

        Returns
        -------
        degf: float
            Degrees of freedom
    '''
    # Non-central t distribution with non-centrality parameter of 0.
    return nctdtridf(1-(1-conf)/2, 0, tp)