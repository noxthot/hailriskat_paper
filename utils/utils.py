import matplotlib.pyplot as plt
import numpy as np

from scipy import stats


def custom_round(x, kernel_size):
    return round(kernel_size * x) / kernel_size


def wormplot(actual, predicted):
    err = actual - predicted

    q = (err.rank() - .5) / len(err)
    theoretical = stats.norm.ppf(q) 

    z = np.linspace(-4.0, 4.0, num=500)
    se = (np.sqrt(stats.norm.cdf(z) * (1 - stats.norm.cdf(z)) / len(err)) / stats.norm.pdf(z)) * np.std(err)

    fig = plt.figure()
    plt.scatter(theoretical, err - (np.mean(err) + theoretical * np.std(err)), color = 'k')
    plt.plot(z, 2 * se, color = 'r')
    plt.plot(z, -2 * se, color = 'r')
    plt.xlabel('Theoretical Quantiles')
    plt.ylabel('Deviance')
    plt.title('Wormplot of the residues')

    return fig