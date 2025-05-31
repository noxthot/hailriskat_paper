import numdifftools as nd
import numpy as np

from scipy import stats


def M1(real):
    n = len(real)
    ret = 1 / (n * (n - 1)) * sum(np.sort(real) * list(range(n - 1 ,-1, -1)))
    return ret


def paramest(data):
    def log_likelihood(params):
        ret = -stats.weibull_min.logpdf(data, c = params[0], scale=params[1]).sum()
        return ret
    
    Hfun = nd.Hessian(log_likelihood)

    params = stats.weibull_min.fit(np.array(data), floc=0)
    vcov = np.linalg.inv(Hfun([params[0], params[2]]))

    return params[0], params[2], vcov


def rl_grad(p, C, k, n):
    ret_1 = -C / (k ** 2) * (-np.log(1 - p ** (1 / n))) ** (1 / k) * np.log(-np.log(1 - p ** (1 / n)))
    ret_2 = (-np.log(1 - p ** (1 / n))) ** (1 / k)

    return np.array([ret_1, ret_2])


def weighted_inner(h, vcov):
    return np.dot(h, np.dot(vcov, h))
