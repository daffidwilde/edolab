""" Tests for the `run` command helper functions. """

import edo

from edolab.run import (
    get_default_optimiser_arguments,
    get_experiment_parameters,
)

from .experiment import fitness, NegativeUniform


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

    params = get_experiment_parameters("tests.experiment")
    expected = {
        "fitness": fitness,
        "size": 10,
        "row_limits": [1, 5],
        "col_limits": [1, 2],
        "weights": None,
        "max_iter": 5,
        "best_prop": 0.1,
        "lucky_prop": 0,
        "crossover_prob": 0.5,
        "mutation_prob": 0.5,
        "shrinkage": None,
        "maximise": False,
    }

    for key, val in params.items():
        if key != "families":
            exp = expected[key]
            assert exp == val
        else:
            families = val
            for fam in families:
                assert isinstance(fam, edo.Family)

            assert [fam.distribution for fam in families] == [
                edo.distributions.Uniform,
                NegativeUniform,
            ]
