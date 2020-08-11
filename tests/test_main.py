""" Tests for the commands in the main script. """

import os
import pathlib

import numpy as np
import pandas as pd
import pytest
from click.testing import CliRunner

from edolab.__main__ import main
from edolab.version import __version__

here = pathlib.Path(f"{__file__}").parent


def test_main_gives_help_info():
    """ Test that the main function runs without issue. """

    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0

    with pytest.raises(SystemExit) as e:
        assert result.output == str(main())
        assert isinstance(e, SystemExit)
        assert e.value == 0


def test_main_gives_version():
    """ Test that the main function gives the current version when asked. """

    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert result.output == __version__ + "\n"


def test_run_writes_to_file(tmpdir):
    """ Test that the `run` command writes something to file. """

    there = pathlib.Path(tmpdir)
    os.system(f"cp {here / 'experiment.py'} {there}")

    runner = CliRunner()
    result = runner.invoke(main, ["run", f"{there / 'experiment.py'}"],)
    assert result.exit_code == 0

    out = pathlib.Path(tmpdir) / "experiment"
    assert [p.name for p in out.iterdir()] == ["data"]

    data = out / "data"
    assert [p.name for p in data.iterdir()] == ["0"]

    trial = data / "0"
    assert {p.name for p in trial.iterdir()} == {
        "0",
        "1",
        "2",
        "3",
        "subtypes",
        "fitness.csv",
    }


def test_run_runs_without_issue_in_parallel(tmpdir):
    """ We know that EDO runs fine in parallel so just check the CLI runs with
    multiple cores. """

    there = pathlib.Path(tmpdir)
    os.system(f"cp {here / 'experiment.py'} {there}")

    runner = CliRunner()
    result = runner.invoke(
        main, ["run", "--cores=4", f"{there / 'experiment.py'}"],
    )
    assert result.exit_code == 0


def test_run_makes_fitnesses_as_expected(tmpdir):
    """ Test that the fitness output is as expected. """

    there = pathlib.Path(tmpdir)
    os.system(f"cp {here / 'experiment.py'} {there}")

    runner = CliRunner()
    _ = runner.invoke(main, ["run", f"{there / 'experiment.py'}"])

    fitness = pd.read_csv(there / "experiment" / "data" / "0" / "fitness.csv")
    expected = pd.read_csv(here / "experiment" / "data" / "0" / "fitness.csv")

    assert all(fitness.columns == expected.columns)
    assert np.allclose(fitness, expected)


def test_summarise_writes_to_file(tmpdir):
    """ Test that the `summarise` command writes something to file. """

    out = pathlib.Path(tmpdir)
    os.system(f"cp -r {here / 'experiment'} {out}")

    runner = CliRunner()
    result = runner.invoke(
        main, ["summarise", f"{here / 'experiment.py'}", f"{out}"]
    )
    assert result.exit_code == 0

    out = out / "experiment"
    assert [p.name for p in out.iterdir()] == ["data", "summary"]

    summary = out / "summary"
    assert {p.name for p in summary.iterdir()} == {"0", "0.5", "1", "main.csv"}

    for quantile in ("0", "0.5", "1"):
        quantile = summary / quantile
        assert {p.name for p in quantile.iterdir()} == {
            "README",
            "main.csv",
            "main.meta",
            "main.state",
        }


def test_summarise_makes_summary_as_expected(tmpdir):
    """ Test that the summary output is as expected. """

    out = pathlib.Path(tmpdir)
    os.system(f"cp -r {here / 'experiment'} {out}")

    runner = CliRunner()
    _ = runner.invoke(
        main, ["summarise", f"{here / 'experiment.py'}", f"{out}"]
    )

    summary = pd.read_csv(out / "experiment" / "summary" / "main.csv")
    expected = pd.read_csv(here / "experiment" / "summary" / "main.csv")

    assert all(summary.columns == expected.columns)
    assert np.allclose(summary, expected)


def test_summarise_can_make_tarball(tmpdir):
    """ Test that the `summarise` command can compress the data when asked. """

    out = pathlib.Path(tmpdir)
    os.system(f"cp -r {here / 'experiment'} {out}/")

    os.system(f"edolab summarise --tarball {here / 'experiment.py'} {tmpdir}")

    out = out / "experiment"
    assert {p.name for p in out.iterdir()} == {"data.tar.gz", "summary"}
