""" Tests for the `run` command helper functions. """

import inspect
import pathlib

import edo
from dask.delayed import Delayed
from edo.distributions import Uniform

from edolab.run import (
    get_default_optimiser_arguments,
    get_experiment_parameters,
    run_single_trial,
)

from .experiment import CustomOptimiser, NegativeUniform, fitness


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
        "root": None,
        "processes": None,
        "fitness_kwargs": None,
        "stop_kwargs": None,
        "dwindle_kwargs": None,
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
        "optimiser": CustomOptimiser,
        "root": None,
        "processes": None,
        "fitness_kwargs": {"size": 3},
        "stop_kwargs": {"tol": 1e-3},
        "dwindle_kwargs": {"rate": 10},
    }

    for key, val in params.items():
        if key == "fitness":
            assert val.__doc__ == fitness.__doc__
            assert inspect.signature(val) == inspect.signature(fitness)

        elif key == "optimiser":
            assert val.__doc__ == CustomOptimiser.__doc__
            assert inspect.signature(val) == inspect.signature(CustomOptimiser)
            assert val.run is CustomOptimiser.run

            for method in ("stop", "dwindle"):
                assert inspect.signature(
                    vars(val)[method]
                ) == inspect.signature(vars(CustomOptimiser)[method])
                assert (
                    vars(val)[method].__doc__
                    == vars(CustomOptimiser)[method].__doc__
                )

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


def test_run_single_trial(tmpdir):
    """ Test that the single trial runner produces a valid set of results. """

    here = pathlib.Path(f"{__file__}").parent
    experiment = here / "experiment.py"
    root = pathlib.Path(tmpdir)
    out = root / "experiment"
    data = out / "data"
    trial = data / "0"

    task = run_single_trial(experiment, data, seed=0)
    assert isinstance(task, Delayed)

    _ = task.compute()
    assert [p.name for p in out.iterdir()] == ["data"]
    assert [p.name for p in data.iterdir()] == ["0"]
    assert {p.name for p in trial.iterdir()} == {
        "0",
        "1",
        "2",
        "3",
        "subtypes",
        "fitness.csv",
    }
