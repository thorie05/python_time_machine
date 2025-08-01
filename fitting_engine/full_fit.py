from .bayesian_fit import bayesian_fit
from .bootstrap_fit import bootstrap_fit
from .get_initial_guess import get_initial_guess


def full_fit(x_data, y_data, y_err_std, model_function, known_params,
    known_params_err_std=None, free_params_priors=None, bounds=None,
    only_positive=False, cores=4, quality="medium", verbose=False, seed=None,
    status_callback=None):
    """Full fit function that combines bootstrap and bayesian fit.
    
    A wrapper function for the bayesian fit, that estimates free parameter
    priors using the bootstrap fit, if not already provided. It also exposes
    more straightforward quality settings, namely 'low', 'medium' and 'high'
    that affect the quality of the results and run-time.

    Args:
        x_data (numpy.ndarray): The x-values of the data points.
        y_data (numpy.ndarray): The y-values of the data points.
        y_err_std (numpy.ndarray): The standard deviation of the y-values.
        model_function (callable): The model function to be used for fitting.
        known_params (dict(str: float or numpy.ndarray)): Dict mapping the known
            parameter names to their known values. If an array is passed it
            has to have the same length as the number of data points.
        known_params_err_std (dict(str: float), optional): An optional dict
            mapping the known parameter names to standard deviation of their
            uncertain known values.
        free_params_priors (dict(str: Tuple(float, float)), optional): An
            optional dict mapping the free parameter names to a tuple containing
            the most likely value e.g. initial guess along with the expected
            standard deviation. If not provided, it is estimated with a
            bootstrap fit.
        bounds (dict(str: Tuple(float, float)), optional): An optional dict
            mapping the free parameter names to a tuple containing the lower and
            upper bounds of the free paremters. Only used to obtain the initial
            guess for the bootstrap fit when free_params_priors is not provided.
            If no bounds are given, bounds from -1e6 to 1e6 or from 0 to 1e6 are
            assumed depending on the only_positive flag.
        only_positive (bool, optional): Optional flag that controls if the fit
            parameters are allowed to be only positive.
        n_bootstrap (int, optional): Optional number of bootstrap samples for
            prior estimation.
        cores (int, optional): Optional number of cores to use.
        quality (str, optional): Optional string determining the quality of the
            fit result. Higher quality needs more run-time. Values can be either
            'low', 'medium', 'high' or 'very high'. The standard value is
            'medium'.
        verbose (bool, optional): Optional flag controling console output.
        seed (int, optional): Optional random number generator seed.
        status_callback (callable, optional): A callable that receives
            human-readable status updates at key points in the fitting pipeline.
            Can be used to update UI text or logs.

    Returns:
        FitResult: Dataclass containing all relevant information about a fit.
        See documentation for details.
    """

    # fit quality settings
    if quality.lower() == "low":
        draws = 3_000
        tune = 1_000
        target_accept = 0.9
        n_bootstrap = 1_000
    elif quality.lower() == "medium":
        draws = 10_000
        tune = 2_000
        target_accept = 0.95
        n_bootstrap = 2_500
    elif quality.lower() == "high":
        draws = 20_000
        tune = 4_000
        target_accept = 0.99
        n_bootstrap = 5_000
    else:
        draws = 100_000
        tune = 10_000
        target_accept = 0.999
        n_bootstrap = 10_000

    # if no free parameter priors given get the estimates with a bootstrap fit
    if not free_params_priors:
        if status_callback:
            status_callback("Finding initial guess...")

        # get the initial guess for the bootstrap fit
        initial_guess = get_initial_guess(x_data, y_data, model_function,
            known_params, bounds=bounds, y_err_std=y_err_std,
            only_positive=only_positive)

        if status_callback:
            status_callback("Estimating priors with Bootstrap...")

        # perform a bootstrap fit to obtain free parameter prior estimates
        bootstrap_fit_result = bootstrap_fit(n_bootstrap, x_data, y_data,
            model_function, known_params, initial_guess, y_err_std=y_err_std,
            known_params_err_std=known_params_err_std,
            only_positive=only_positive, cores=cores, seed=seed)

        free_params_priors = {}
        for param_name, param_best_fit in bootstrap_fit_result.best_fit.items():
            lower, upper = bootstrap_fit_result.confidence_interval[param_name]
            # Take max distance to 95% confidence interval as the prior std.
            # For gaussian, symmetric distributions this is equivalent to
            # doubling the standard deviation, for non symmetric distributions
            # the larger distance is taken to ensure a conservative guess.
            # If bootstrap gives far too large confidence intervals then a
            # maximum relative standard deviation of 1 is used.
            prior_std = max(param_best_fit - lower, upper - param_best_fit)
            prior_std = min(prior_std, param_best_fit)
            free_params_priors[param_name] = (param_best_fit, prior_std)

    if status_callback:
        status_callback("Running MCMC Bayesian fit...")

    # perform bayesian fit
    bayesian_fit_result = bayesian_fit(draws, tune, x_data, y_data,
        model_function, known_params, free_params_priors, y_err_std,
        known_params_err_std=known_params_err_std, only_positive=only_positive,
        target_accept=target_accept, verbose=verbose, seed=seed)

    # return the result object containing posterior samples and fit statistics
    return bayesian_fit_result
