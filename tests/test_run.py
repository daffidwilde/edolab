""" Tests for the `run` command helper functions. """

import inspect
import pathlib

import edo
from edo.distributions import Uniform

from edolab.run import (
    get_default_optimiser_arguments,
    get_experiment_parameters,
)

from .experiment import NegativeUniform, fitness


def test_get_default_optimiser_parameters():
    """ Test that the correct defaults are returned. """

    defaults = get_default_optimiser_arguments()
    expected = {
        "weights": None,
        "max_iter": 100,
        "best_prop": 0.25,
        "lucky_prop": 0,
        "crossover_prob": 0.5,
        "mutation_prob": 0.01,
        "shrinkage": None,
        "maximise": False,
    }

    assert defaults == expected


def test_get_experiment_parameters():
    """ Test that the correct parameters can be brought over from an experiment
    script. """

    here = pathlib.Path(f"{__file__}").parent
    params = get_experiment_parameters(here / "experiment.py")
    expected = {
        "size": 5,
        "row_limits": [1, 5],
        "col_limits": [1, 2],
        "weights": None,
        "max_iter": 3,
        "best_prop": 0.5,
        "lucky_prop": 0,
        "crossover_prob": 0.5,
        "mutation_prob": 0.5,
        "shrinkage": None,
        "maximise": False,
    }

    for key, val in params.items():
        if key == "fitness":
            assert val.__doc__ == fitness.__doc__
            assert inspect.signature(val) == inspect.signature(fitness)

        elif key == "families":
            families = val
            for fam, dist in zip(families, [Uniform, NegativeUniform]):
                distribution = fam.distribution
                assert isinstance(fam, edo.Family)
                assert distribution.__doc__ == dist.__doc__
                assert distribution.name == dist.name
                assert distribution.param_limits == dist.param_limits
                assert distribution.hard_limits == dist.hard_limits
                assert distribution.sample is dist.sample

        else:
            exp = expected[key]
            assert exp == val
