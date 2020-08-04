""" Placeholder parameters. """

import numpy as np
from edo.distributions import Uniform


def fitness(individual, size=3, seed=0):
    """ Randomly sample `size` values from an individual and return the
    minimum. """

    np.random.seed(seed)
    values = individual.dataframe.values.flat
    sample = np.random.choice(values, size=size)
    return min(sample)


class NegativeUniform(Uniform):
    """ A copy that only takes negative values. """

    name = "NegativeUniform"
    param_limits = {"bounds": [-1, 0]}
    hard_limits = {"bounds": [-100, 0]}


Uniform.param_limits["bounds"] = [0, 1]

size = 5
row_limits = [1, 5]
col_limits = [1, 2]
max_iter = 3
best_prop = 0.5
mutation_prob = 0.5
distributions = [Uniform, NegativeUniform]
