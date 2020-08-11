# edolab

![CI](https://github.com/daffidwilde/edolab/workflows/CI/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3972301.svg)](https://doi.org/10.5281/zenodo.3972301)

A command line tool for running experiments with
[`edo`](https://github.com/daffidwilde/edo).


## Installation

`edolab` is `pip`-installable:

```
$ python -m pip install edolab
```


## Usage

### Experiment scripts

To use `edolab`, you will need to write a Python script configuring the
parameters of your experiment.

#### Required parameters

- `fitness`: A function that takes (at least) an `edo.Individual` instance
  to be used as the fitness function by `edo`
- `distributions`: A list of `edo.distribution.Distribution` subclasses that
  will be used to create the `edo.Family` instances for `edo`
- Variable assignments for all of the essential arguments in
  `edo.DataOptimiser` except for `families`

#### Optional parameters

- `root`: A directory to which data should be written (and summarised from)
- `processes`: A number of processes for `edo` to use when calculating
  population fitness
- Custom column distribution classes should be defined in the script
- If you wish to use a custom `stop` or `dwindle` method then define a subclass
  of `edo.DataOptimiser` and assign that class to a variable called `optimiser`
- Any keyword arguments to pass to `fitness` or the `stop` and `dwindle` methods
  should be assigned to the corresponding `<func>_kwargs` variable.

An example of such a script would be something like this:

```python
""" /path/to/experiment/script.py """

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
```

For more details on the parameters of `edo`, see its documentation:
<https://edo.readthedocs.io>

### Running the experiment

Then, to run an experiment with this script do the following:

```
$ edolab run /path/to/experiment/script.py
```

### Summarising the experiment

And to summarise the data (for easy transfer):

```
$ edolab summarise /path/to/experiment/script.py
```

For further details on the commands, use the `--help` flag on the `run` and
`summarise` commands.

### A note on reproducibility

It is highly recommended that you use a virtual environment when using `edo` in
or outside of this command line tool as `edo` uses `pickle` to store various
objects created in a run that may not be retrievable with a different version of
Python.


## Contributing

This tool has been made to be pretty bare and could use some padding out. If
you'd like to contribute then make a fork and clone the repository locally:

```
$ git clone https://github.com/<your-username>/edolab.git
```

Install the package and replicate the `conda` environment (or install the
development dependencies manually):

```
$ cd edolab
$ python setup.py develop
$ conda env create -f environment.yml
$ conda activate edolab-dev
```

Make your changes and write tests to go with them, ensuring they pass:

```
$ python -m pytest --cov=edolab --cov-fail-under=100 tests
```

Commit, push to your fork and open a pull request!
