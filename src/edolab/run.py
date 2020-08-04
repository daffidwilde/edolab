""" Helper functions for the `run` command. """

import importlib
import inspect

import edo


def get_default_optimiser_arguments():
    """ Get the default arguments from `edo.DataOptimiser`. """

    signature = inspect.signature(edo.DataOptimiser)

    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def get_experiment_parameters(name):
    """ Get the parameters for the experiment. """

    module = {
        k.lower(): v for k, v in vars(importlib.import_module(name)).items()
    }

    module_params = {
        k: v
        for k, v in module.items()
        if k in inspect.getfullargspec(edo.DataOptimiser).args
    }

    distributions = module["distributions"]
    families = [edo.Family(distribution) for distribution in distributions]
    module_params["families"] = families

    params = get_default_optimiser_arguments()
    params.update(module_params)
    return params
