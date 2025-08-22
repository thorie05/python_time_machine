from .bayesian_fit import bayesian_fit
from .bootstrap_fit import bootstrap_fit
from .get_initial_guess import get_initial_guess
from .fit_quality_settings import fit_quality_settings


def full_fit(x_data, y_data, y_err_std, model_function, known_params,
    known_params_err_std=None, free_params_priors=None, bounds=None,
    fit_quality=fit_quality_settings.medium, only_positive=False, cores=4,
    seed=None, status_callback=None, verbose=False):
    """Full fit function that combines bootstrap and bayesian fit.
    
    A wrapper function for the bayesian fit, that estimates free parameter
    priors using the bootstrap fit, if not already provided. It also exposes
    more straightforward quality settings, namely 'low', 'medium', 'high'
    and 'very high' that affect the quality of the results and the run-time. See
    fit_quality_settings for details.

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
        fit_quality (Low, Medium, High, VeryHigh, optional): Optional dataclass
            determining the quality of the fit result. See FitQualitySettings
            for details.
        only_positive (bool, optional): Optional flag that controls if the fit
            parameters are allowed to be only positive.
        cores (int, optional): Optional number of cores to use.
        seed (int, optional): Optional random number generator seed.
        status_callback (callable, optional): A callable that receives
            human-readable status updates at key points in the fitting pipeline.
            Can be used to update UI text or logs.
        verbose (bool, optional): Optional flag controling console output.

    Returns:
        FitResult: Dataclass containing all relevant information about a fit.
            See documentation for details.
    """

    # extract quality variables from the fit quality dataclass
    num_restarts = fit_quality.num_restarts
    n_bootstrap = fit_quality.n_bootstrap
    draws = fit_quality.draws
    tune = fit_quality.tune
    target_accept = fit_quality.target_accept

    # if no free parameter priors given get the estimates with a bootstrap fit
    if not free_params_priors:
        # update status text for gui
        if status_callback:
            status_callback("Finding initial guess...")

        # get the initial guess for the bootstrap fit
        workers = cores if cores else -1
        initial_guess = get_initial_guess(x_data, y_data, model_function,
            known_params, bounds=bounds, y_err_std=y_err_std,
            only_positive=only_positive, num_restarts=num_restarts,
            workers=workers)

        # update status text for gui
        if status_callback:
            status_callback("Estimating priors with Bootstrap...")

        # perform a bootstrap fit to obtain free parameter prior estimates
        bootstrap_fit_result = bootstrap_fit(n_bootstrap, x_data, y_data,
            model_function, known_params, initial_guess, y_err_std=y_err_std,
            known_params_err_std=known_params_err_std,
            only_positive=only_positive, cores=cores, seed=seed)

        # validate bootstrap success
        if not bootstrap_fit_result.success:
            raise RuntimeError("Bootstrap run was not successful.")

        # use bootstrap results as bayesian priors for the mcmc fit
        free_params_priors = {}
        for param_name, param_best_fit in bootstrap_fit_result.best_fit.items():
            lower, upper = bootstrap_fit_result.confidence_interval[param_name]
            # Take max distance to 95% confidence interval as the prior std.
            # For gaussian, symmetric distributions this is equivalent to
            # doubling the standard deviation, for non symmetric distributions
            # the larger distance is taken to ensure a conservative guess.
            # If bootstrap gives far too large confidence intervals because of
            # numerical instability then a maximum relative standard deviation
            # of 1 is used, to ensure a very conservative guess.
            prior_std = max(param_best_fit - lower, upper - param_best_fit)
            prior_std = min(prior_std, param_best_fit)
            free_params_priors[param_name] = (param_best_fit, prior_std)

    # update status text for gui
    if status_callback:
        status_callback("Running MCMC Bayesian fit...")

    # perform bayesian fit
    bayesian_fit_result = bayesian_fit(draws, tune, x_data, y_data, y_err_std,
        model_function, known_params, free_params_priors,
        known_params_err_std=known_params_err_std, only_positive=only_positive,
        target_accept=target_accept, seed=seed, verbose=verbose)

    # initial guess, bootstrap fit results and the result object containing
    # posterior samples and fit statistics
    return initial_guess, bootstrap_fit_result, bayesian_fit_result
