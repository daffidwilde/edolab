""" Helper functions for the `run` command. """

import importlib
import inspect

import dask
import edo


def get_default_optimiser_arguments():
    """ Get the default arguments from `edo.DataOptimiser`. """

    signature = inspect.signature(edo.DataOptimiser)
    defaults = {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }

    defaults["root"] = None
    defaults["processes"] = None
    defaults["fitness_kwargs"] = None
    defaults["stop_kwargs"] = None
    defaults["dwindle_kwargs"] = None

    return defaults


def get_experiment_parameters(experiment):
    """ Get the parameters for the experiment. """

    spec = importlib.util.spec_from_file_location("__main__", experiment)
    experiment = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(experiment)

    module = {k.lower(): v for k, v in vars(experiment).items()}

    all_params = set(inspect.getfullargspec(edo.DataOptimiser).args) | set(
        inspect.getfullargspec(edo.DataOptimiser.run).args
    )

    module_params = {k: v for k, v in module.items() if k in all_params}

    module_params["families"] = [
        edo.Family(dist) for dist in module["distributions"]
    ]
    module_params["optimiser"] = module.get("optimiser", edo.DataOptimiser)

    params = get_default_optimiser_arguments()
    params.update(module_params)

    return params


@dask.delayed
def run_single_trial(experiment, root, seed):
    """ Lazily run a single trial of an experiment. """

    params = get_experiment_parameters(experiment)

    _ = params.pop("root")
    optimiser = params.pop("optimiser")
    processes = params.pop("processes")
    fitness_kwargs = params.pop("fitness_kwargs")
    stop_kwargs = params.pop("stop_kwargs")
    dwindle_kwargs = params.pop("dwindle_kwargs")

    opt = optimiser(**params)
    _ = opt.run(
        root=root / str(seed),
        processes=processes,
        random_state=seed,
        fitness_kwargs=fitness_kwargs,
        stop_kwargs=stop_kwargs,
        dwindle_kwargs=dwindle_kwargs,
    )
