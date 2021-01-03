""" Placeholder parameters. """

import edo
import numpy as np
from edo.distributions import Uniform


class CustomOptimiser(edo.DataOptimiser):
    """ This is an optimiser with custom stopping and dwindling methods. """

    def stop(self, tol):
        """ Stop if the median fitness is less than `tol` away from zero. """

        self.converged = abs(np.median(self.pop_fitness)) < tol

    def dwindle(self, rate):
        """ Cut the mutation probability in half every `rate` generations. """

        if self.generation % rate == 0:
            self.mutation_prob /= 2


def fitness(individual, size, seed=0):
    """Randomly sample `size` values from an individual and return the
    minimum."""

    np.random.seed(seed)
    values = individual.dataframe.values.flat
    sample = np.random.choice(values, size=size)
    return min(sample)


class NegativeUniform(Uniform):
    """ A copy that only takes negative values. """

    name = "NegativeUniform"
    param_limits = {"bounds": [-1, 0]}
    hard_limits = {"bounds": [-100, 0]}


size = 5
row_limits = [1, 5]
col_limits = [1, 2]
max_iter = 3
best_prop = 0.5
mutation_prob = 0.5

Uniform.param_limits["bounds"] = [0, 1]

distributions = [Uniform, NegativeUniform]
optimiser = CustomOptimiser

fitness_kwargs = {"size": 3}
stop_kwargs = {"tol": 1e-3}
dwindle_kwargs = {"rate": 10}
