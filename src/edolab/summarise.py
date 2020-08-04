""" Helper functions for the `summarise` command. """

import importlib
import os

import edo
import numpy as np
import pandas as pd


def get_distributions(experiment):
    """ Get the distribution classes used in the experiment. """

    spec = importlib.util.spec_from_file_location("__main__", experiment)
    experiment = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(experiment)

    return experiment.distributions


def get_trial_summary(trial, distributions):
    """ Summarise a trial by recording the origins, shapes, sizes and fitnesses
    of the individuals created in that trial. """

    fitness = pd.read_csv(trial / "fitness.csv")
    max_generation = fitness["generation"].max()

    pop_history = edo.optimiser._get_pop_history(
        trial, max_generation + 1, distributions
    )

    summary_dfs = []
    for gen, generation in enumerate(pop_history):
        generation_summary = []
        for idx, individual in enumerate(generation):

            dataframe = individual.dataframe
            nrows = len(dataframe)
            ncols = len(dataframe.columns)
            size = dataframe.memory_usage().sum().compute()

            generation_summary.append((idx, nrows, ncols, size))

        generation_summary = pd.DataFrame(
            generation_summary,
            columns=["individual", "nrows", "ncols", "memory"],
        )
        generation_summary["generation"] = gen
        summary_dfs.append(generation_summary)

    summary = pd.concat(summary_dfs, axis=0, ignore_index=True)
    summary["fitness"] = fitness["fitness"]
    summary["seed"] = int(trial.stem)

    return summary


def get_representative_idxs(summary, quantiles):
    """ Get the indices of those individuals that have the closest fitness to
    the given quantiles. """

    fitness = summary["fitness"]
    idxs = {}
    for quantile in quantiles:
        diffs = (fitness - fitness.quantile(quantile)).abs().values
        idxs[quantile] = np.argmin(diffs)

    return idxs


def write_representatives(summary, idxs, data_path, summary_path):
    """ Write to file the individuals at the indices given by `idxs`. """

    for quantile, idx in idxs.items():

        gen, ind, seed = map(
            str, summary[["generation", "individual", "seed"]].iloc[idx, :]
        )

        origin = data_path / seed / gen / ind
        out = summary_path / str(quantile)
        out.mkdir(exist_ok=True, parents=True)

        os.system(f"cp -r {origin}/main.* {out}")
        with open(out / "README", "w") as readme:
            readme.write(
                f"Invididual {ind} of generation {gen} in trial {seed}."
            )
