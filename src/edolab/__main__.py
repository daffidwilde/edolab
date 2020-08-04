""" The main script. """

import os
import pathlib
import tarfile

import click
import edo
import pandas as pd
import tqdm

from .run import get_experiment_parameters
from .summarise import (
    get_distributions,
    get_representative_idxs,
    get_trial_summary,
    write_representatives,
)


@click.group()
def main():
    """ Run and summarise experiments with `edo`. """


@main.command()
@click.argument("experiment", type=click.Path(exists=True))
@click.option("--cores", default=None, help="The number of cores to use.")
@click.option("--seeds", default=1, help="The number of trials to run.")
@click.option("--root", default=".", help="The directory to write out to.")
def run(experiment, cores, seeds, root):
    """ Run a series of trials using the `experiment` script. """

    experiment = pathlib.Path(experiment).resolve()
    name = experiment.stem

    click.echo(f"Running experiment: {name}")

    out = pathlib.Path(f"{root}/{name}/data").resolve()
    out.mkdir(exist_ok=True, parents=True)

    click.echo(f"Writing to: {out}")

    for seed in tqdm.tqdm(range(seeds)):
        params = get_experiment_parameters(experiment)
        opt = edo.DataOptimiser(**params)
        _ = opt.run(root=out / str(seed), processes=cores, random_state=seed)

    click.echo("Experiment complete")


@main.command()
@click.option(
    "--tarball/--no-tarball",
    default=False,
    help="Tarball the data and delete original, or don't.",
)
@click.argument("experiment", type=click.Path(exists=True))
@click.argument("root", default=".", type=click.Path(exists=True))
@click.argument("quantiles", nargs=-1, type=float, required=False)
def summarise(tarball, experiment, root, quantiles):
    """ Summarise the EDO data from an experiment.

    Here, `experiment` should be of the form
    `/path/to/experiment/directory/{name}.py` and the data that will be
    summarised is located under `root/{name}`.

    To specify quantiles (between 0 and 1), list them at the end. Defaults to
    the minimum, median and maximum. """

    if not quantiles:
        quantiles = (0, 0.5, 1)

    experiment = pathlib.Path(experiment)

    out = pathlib.Path(root) / experiment.stem
    data = out / "data"
    summary_path = out / "summary"
    summary_path.mkdir(exist_ok=True)

    click.echo(f"Summarising data at {experiment}")

    distributions = get_distributions(experiment)
    trials = (
        path
        for path in data.iterdir()
        if path.is_dir() and path.stem != "subtypes"
    )
    summaries = []
    for trial in tqdm.tqdm(trials):
        summaries.append(get_trial_summary(trial, distributions))

    summary = pd.concat(summaries)
    summary = summary.sort_values(["generation", "individual", "seed"])
    summary.to_csv(summary_path / "main.csv", index=False)

    click.echo("Getting representative individuals")

    idxs = get_representative_idxs(summary, quantiles)
    write_representatives(summary, idxs, data, summary_path)

    if tarball:
        click.echo("Making tarball")

        with tarfile.open(str(data) + ".tar.gz", "w:gz") as tar:
            tar.add(data, arcname=data.stem)

        os.system(f"rm -r {data}")

    click.echo("Summary complete")


if __name__ == "__main__":  # pragma: no cover
    main()
