import numpy as np
import pymc
import arviz
import sys
import os
import contextlib
import logging
from .fit_result_dataclass import FitResult


def bayesian_fit(draws, tune, x_data, y_data, model_function, known_params,
    free_params_priors, y_err_std, known_params_err_std=None,
    only_positive=False, target_accept=0.95, chains=4,
    cores=4, verbose=False, seed=None):
    """
    A fitting function that uses the MCMC method for calculating uncertainties.

    A function that takes datapoints and a mathematical model function to
    calculate the best fit of the model through the datapoints as well as the
    uncertainties for all fitting parameters. Uses the Bayesian MCMC method from
    the PyMC module. If the known_params dict contains arrays with seperate
    values of the parameters for each data point, no perturbation will be
    applied, meaning the parameter is treated as fixed with a 100% certainty for
    every individual data point.

    Args:
        draws (int): Number of MCMC samples per chain.
        tune (int): Number of tuning steps.
        x_data (numpy.ndarray): The x-values of the data points.
        y_data (numpy.ndarray): The y-values of the data points.
        model_function (callable): The model function to be used for fitting.
        known_params (dict(str: float or numpy.ndarray)): Dict mapping the known
            parameter names to their known values. If an array is passed it
            has to have the same length as the number of data points.
        free_params_priors (dict(str: Tuple(float, float))): A dict mapping the
            free parameter names to a tuple containing the most likely value
            e.g. initial guess along with the expected standard deviation.
            Serves as a prior for the MCMC model.
        y_err_std (numpy.ndarray): The standard deviation of the y-values.
        known_params_err_std (dict(str: float), optional): An optional dict
            mapping the known parameter names to standard deviation of their
            uncertain known values.
        only_positive (bool, optional): Optional flag that controls if the fit
            parameters are allowed to be only positive. Enforces the use of the
            truncated normal distribution instead of the usual one.
        target_accept (float): Optional PyMC target_accept argument.
        chains (int, optional): Optional number MCMC chains.
        cores (int, optional): Optional number of cores to use.
        verbose (bool, optional): Optional flag controling console output.
        seed (int, optional): Optional random number generator seed.

    Returns:
        FitResult: Dataclass containing all relevant information about a fit.
            See documentation for details.
    """

    with pymc.Model():
        # define known parameters (with perturbation if std given)
        uncertain_known_params = {}
        for param_name, param_mu in known_params.items():
            # known parameters can be scalar, meaning they are constant fot all
            # data points or numpy arrays, which allows each data point to have
            # individual values for the parameter
            if np.isscalar(param_mu):
                # if standard deviation is provided for the parameter in the
                # known_params_err_std dict add the parameter according to the
                # normal distribution given by its standard deviation
                if known_params_err_std and (param_std \
                    := known_params_err_std.get(param_name, 0)) > 0:
                    if only_positive:
                        uncertain_known_params[param_name] \
                            = pymc.TruncatedNormal(param_name, mu=param_mu,
                            sigma=param_std, lower=0)
                    else:
                        uncertain_known_params[param_name] = pymc.Normal(
                            param_name, mu=param_mu, sigma=param_std)
                # if the parameter isn't in the known_params_err_std_dict or has
                # a standard deviation of 0 treat is as fixed
                else:
                    uncertain_known_params[param_name] = param_mu
            else:
                # if it's a vector, also treat it as fixed, it will be evaluated
                # point-wise
                uncertain_known_params[param_name] = param_mu

        # define priors/free/fit parameters
        priors = {}
        for param_name, (param_mu, param_std) in free_params_priors.items():
            if only_positive:
                priors[param_name] = pymc.TruncatedNormal(param_name,
                    mu=param_mu, sigma=param_std, lower=0)
            else:
                priors[param_name] = pymc.Normal(param_name, mu=param_mu,
                    sigma=param_std)

        # evaluate model function with pymc math
        model_y = model_function(x_data, **uncertain_known_params, **priors,
            math=pymc.math)

        # provide model with observed data and errors
        pymc.Normal("obs", mu=model_y, sigma=y_err_std, observed=y_data)

        # run mcmc
        if not verbose:
            # silence console output and logging
            logging.disable(logging.CRITICAL)
            with no_output():
                trace = pymc.sample(draws=draws, tune=tune,
                    target_accept=target_accept, chains=chains, cores=cores,
                    progressbar=False, random_seed=seed)
        else:
            trace = pymc.sample(draws=draws, tune=tune,
                target_accept=target_accept, chains=chains, cores=cores,
                progressbar=True, random_seed=seed)

    # extract results
    best_fit = {}
    confidence_interval = {}
    robust_std = {}
    posterior_samples = {}

    for param_name in free_params_priors:
        samples = trace.posterior[param_name].values.flatten()
        median = np.median(samples)
        lower, upper = np.percentile(samples, [2.5, 97.5])

        # calculate standard deviation from percentiles to make it more robust
        # and less dependent on outliers
        std = (np.percentile(samples, 84.13) \
            - np.percentile(samples, 15.87)) / 2

        best_fit[param_name] = float(median)
        confidence_interval[param_name] = (float(lower), float(upper))
        robust_std[param_name] = float(std)
        posterior_samples[param_name] = samples

    # fit summary
    summary = arviz.summary(trace, var_names=list(free_params_priors.keys()),
        round_to=None, kind="all")

    # conditions for successful fit
    rhat_ok = np.all(np.abs(summary["r_hat"] - 1) < 0.05)
    ess_ok = np.all(summary["ess_bulk"] > 1000)
    no_divergences = trace.sample_stats["diverging"].values.sum() == 0

    # fit is only successful if all conditions are satisfied
    success = rhat_ok and ess_ok and no_divergences

    result = FitResult(success=success, best_fit=best_fit,
        confidence_interval =confidence_interval, robust_std=robust_std,
        samples=posterior_samples)

    return result


@contextlib.contextmanager
def no_output():
    """Context manager to suppress all stdout and stderr output."""

    with open(os.devnull, 'w') as devnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
