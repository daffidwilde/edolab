""" Tests for the `summarise` command helper functions. """

import pathlib

import numpy as np
import pandas as pd
from edo.distributions import Uniform

from edolab.summarise import (
    get_distributions,
    get_trial_summary,
    get_representative_idxs,
    write_representatives,
)
from .experiment import NegativeUniform


here = pathlib.Path(f"{__file__}").parent


def test_get_distributions():
    """ Test that the distributions are collected from an experiment script
    correctly. """

    distributions = get_distributions(here / "experiment.py")

    for dist, expected in zip(distributions, [Uniform, NegativeUniform]):
        assert dist.__doc__ == expected.__doc__
        assert dist.name == expected.name
        assert dist.param_limits == expected.param_limits
        assert dist.hard_limits == expected.hard_limits
        assert dist.sample is expected.sample


def test_get_trial_summary():
    """ Check that the summary found is as expected. """

    trial = here / "experiment/data/0"
    distributions = [Uniform, NegativeUniform]

    summary = get_trial_summary(trial, distributions)
    expected = pd.read_csv(here / "experiment/summary/main.csv")

    assert list(summary.columns) == [
        "individual",
        "nrows",
        "ncols",
        "memory",
        "generation",
        "fitness",
        "seed",
    ]
    assert np.allclose(summary, expected)


def test_get_representative_idxs():
    """ Test that the representative individuals are located correctly. """

    summary = pd.read_csv(here / "experiment/summary/main.csv")
    quantiles = (0, 0.25, 0.5, 0.75, 1)

    idxs = get_representative_idxs(summary, quantiles)
    assert list(idxs.keys()) == list(quantiles)

    last = -np.infty
    for idx in idxs.values():
        fit = summary["fitness"].iloc[idx]
        assert fit > last
        last = fit


def test_write_representatives(tmpdir):
    """ Test that individuals can be written correctly. """

    summary = pd.read_csv(here / "experiment/summary/main.csv")
    data = here / "experiment/data"
    out = pathlib.Path(tmpdir)
    idxs = {i: i ** 2 for i in range(5)}

    write_representatives(summary, idxs, data, out)

    for i in idxs:
        assert (
            sorted(path.name for path in (out / str(i)).iterdir()) == [
                "README", "main.csv", "main.meta", "main.state"
            ]
        )
