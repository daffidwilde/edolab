# edolab

![CI](https://github.com/daffidwilde/edolab/workflows/CI/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A command line tool for running experiments with `edo`.


## Installation

`edolab` is `pip`-installable:

```
$ python -m pip install edolab
```


## Usage

To use `edolab`, you need a Python script for your experiment and a place to
send the generated data. An valid script must contain:

- a function `fitness` that takes an `edo.Individual` instance to be used as the
  fitness function
- variable assignments for (at least) the essential arguments in
  `edo.DataOptimiser` except for families
- definitions of any custom distribution classes to be used
- a list `distributions` that will be used to create the families

An example of such a script would be something like this:

```python
""" /path/to/experiment/script.py """

from edo.distributions import Uniform


def fitness(individual):
    """ Return the square of the first element of the dataset. """

    return individual.dataframe.iloc[0, 0] ** 2


class MyUniform(Uniform):
    """ A copy of Uniform for demonstrative purposes. """

    name = "MyUniform"
    param_limits = {"bounds": [-1, 1]}


size = 100
row_limits = [1, 1]
col_limits = [1, 1]
max_iter = 5
best_prop = 0.25
distributions = [MyUniform]
```

For more details on the parameters of `edo`, see its documentation at:
<https://edo.readthedocs.io>

Then, to run an experiment with this script do the following:

```
$ edolab run --root="out" /path/to/experiment/script.py
```

And to summarise the data (for easy transfer):

```
$ edolab summarise /path/to/experiment/script.py out
```

For further details, use the `--help` flag on `run` and `summarise` commands.


## Contributing

This tool has been made to be pretty bare and could use some padding out. If
you'd like to contribute then make a fork and clone the repository locally:

```
$ git clone https://github.com/<your-username>/edolab.git
```

Install the package and, optionally, replicate the `conda` environment:

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
