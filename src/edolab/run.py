""" Helper functions for the `run` command. """

import importlib
import inspect

import edo


def get_default_optimiser_arguments():
    """ Get the default arguments from `edo.DataOptimiser`. """

    signature = inspect.signature(edo.DataOptimiser)
    defaults = {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }

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
