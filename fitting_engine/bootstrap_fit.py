import numpy as np
from scipy.stats import truncnorm
from joblib import Parallel, delayed
from .easy_fit import easy_fit
from .fit_result_dataclass import FitResult


def bootstrap_fit(n, x_data, y_data, model_function, known_params,
    initial_guess, y_err_std=None, known_params_err_std=None,
    only_positive=False, cores=-1, seed=None):
    """A fitting function that uses the bootstrap method to estimate errors. 

    A function that takes datapoints and a mathematical model function to
    calculate the least squares best fit of the model through the datapoints and
    more importantly estimate the uncertainty of the calculated values. It
    makes use of the bootstrap method, so it internally calls the easy fit
    function n times, making it quite time-consuming. It works on all cores in
    parallel. If the known_params dict contains arrays with separate values of
    the parameters for each data point, no perturbation will be applied, meaning
    the parameter is treated as fixed with a 100% certainty for every individual
    data point.The results for the fitted parameters are slightly more accurate
    than the results obtained by only using the easy fit function, but only if n
    is sufficiently large enough (e.g. at least 1_000, 10_000 is best). The
    bayesian fit is even more accurate than the bootstrap fit, so it should
    always be used for reliable results. However, the bootstrap fit can serve as
    an estimator.

    Args:
        n (int): Number of bootstrap samples.
        x_data (numpy.ndarray): The x-values of the data points.
        y_data (numpy.ndarray): The y-values of the data points.
        model_function (callable): The model function to be used for fitting.
        known_params (dict(str: float or numpy.ndarray)): Dict mapping the known
            parameter names to their known values. If an array is passed it
            has to have the same length as the number of data points.
        initial_guess (dict(str: float)): Dict mapping the free parameters names
            to their initial guesses.
        y_err_std (numpy.ndarray, optional): The standard deviation of the
            y-values.
        known_params_err_std (dict(str: float), optional): An optional dict
            mapping the known parameter names to the standard deviation of their
            uncertain known values.
        only_positive (bool, optional): Optional flag that controls if the fit
            parameters are allowed to be only positive.
        cores (int, optional): Optional number of cores to use.
        seed (int, optional): Optional random number generator seed.

    Returns:
        FitResult: Dataclass containing all relevant information about a fit.
        See documentation for details.
    """

    rng = np.random.default_rng(seed)

    # make unique seeds of size n for each worker
    seeds = rng.integers(low=0, high=np.iinfo(np.uint64).max, size=n,
        dtype=np.uint64)

    parallel_results = Parallel(n_jobs=cores, batch_size="auto") (
        delayed(single_bootstrap_iteration)(seed_i, x_data, y_data,
        model_function, known_params, initial_guess, y_err_std,
        known_params_err_std, only_positive=only_positive) \
        for seed_i in seeds)

    # set up dict that will store the result of each fit
    bootstrap_samples = {param_name: [] for param_name in initial_guess.keys()}

    # fill the fitting results dict with the results from the parallel execution
    for parallel_result in parallel_results:
        # skip failed bootstrap samples
        if parallel_result is None or (res := parallel_result.best_fit) is None:
            continue
        for param_name, value in res.items():
            bootstrap_samples[param_name].append(value)

    best_fit_dict = {}
    confidence_interval_dict = {}
    robust_std_dict = {}

    # calculate the number of successful bootstrap samples
    try:
        num_successful = len(next(iter(bootstrap_samples.values())))
    except StopIteration:
        num_successful = 0

    # only return success if there are more than 30 successful samples and the
    # success rate is larger than 95%
    success = False
    if num_successful > 0.95 * n and num_successful > 30:
        success = True

    if num_successful > 0:
        for param_name, values in bootstrap_samples.items():
            values = np.array(values)

            # if theoretically all bootstrap iterations fail for a parameter
            # return None for every metric
            if len(values) == 0:
                best_fit_dict[param_name] = None
                confidence_interval_dict[param_name] = None
                robust_std_dict[param_name] = None
                continue

            # median instead of mean for fit results as it can be more stable
            best_fit_dict[param_name] = np.median(values)

            # calculate lower and upper percentile for 95% confidence range
            # instead of standard deviation since the error can be asymetric
            lower_percentile = np.percentile(values, 2.5)
            upper_percentile = np.percentile(values, 97.5)
            confidence_interval_dict[param_name] = \
                (float(lower_percentile), float(upper_percentile))

            # calculate robust standard deviation calculated from the
            # percentiles instead of the normal way to avoid obscuring the
            # results with unplausible outliers
            robust_std_dict[param_name] = float((np.percentile(values, 84.13) \
                - np.percentile(values, 15.87))) / 2

    # construct fit result dataclass to be returned
    fit_result = FitResult(success=success, best_fit=best_fit_dict,
        confidence_interval=confidence_interval_dict,
        robust_std=robust_std_dict, samples=bootstrap_samples)

    return fit_result


def single_bootstrap_iteration(seed, x_data, y_data, model_function,
    known_params, initial_guess, y_err_std=None, known_params_err_std=None,
    only_positive=False):
    """
    A function executing an iteration of the bootstrap method.

    Args:
        seed (int): Random number generator seed.
        x_data (numpy.ndarray): The x-values of the data points.
        y_data (numpy.ndarray): The y-values of the data points.
        model_function (callable): The model function to be used for fitting.
        known_params (dict(str: float or numpy.ndarray)): Dict mapping the known
            parameter names to their known values. The values are allowed to be
            different for each data point.
        initial_guess (dict(str: float)): Dict mapping the free parameters names
            to their initial guesses.
        y_err_std (numpy.ndarray, optional): The standard deviation of the
            y-values.
        known_params_err_std (dict(str: float), optional): An optional dict
            mapping the known parameter names to standard deviation of their
            uncertain known values.
        only_positive (bool, optional): Optional flag that controls if the fit
            parameters are allowed to be only positive.

    Returns:
        dict (str: float): A dict containing the best fit values for each
            parameter.
    """

    rng = np.random.default_rng(seed)

    # randomly choose a new sample of data points
    random_indices = rng.choice(len(x_data), size=len(x_data), replace=True)

    # if too few data points survive discard the sample since it makes no
    # sense to curve fit through too few points
    if len(np.unique(random_indices)) < 2 * len(initial_guess.keys()):
        return None

    x_data_resampled = x_data[random_indices]
    y_data_resampled = y_data[random_indices]
    y_err_std_resampled = None if y_err_std is None \
        else y_err_std[random_indices]

    # if standard deviations for the known parameters are provided perturb
    # each accordingly using the normal distribuation
    # if known values are point-dependent -> no perturbation
    known_params_perturbed = {}
    for param_name, param_value in known_params.items():
        if np.isscalar(param_value):
            # scalar value -> perturb if sigma is given
            if param_std := known_params_err_std.get(param_name):
                # perturb according to given standard deviation
                if only_positive:
                    # truncated normal distribution -> only positive values
                    perturbed = truncnorm(a=-param_value / param_std, b=np.inf,
                        loc=param_value, scale=param_std).rvs(random_state=rng)
                else:
                    # normal distribution
                    perturbed = rng.normal(loc=param_value, scale=param_std) 
                known_params_perturbed[param_name] = perturbed
            else:
                # if no standard deviations are provided for each parameter
                # don't perturb them -> only resampling
                known_params_perturbed[param_name] = param_value

        else:
            # array -> just resample, no perturbation
            known_params_perturbed[param_name] = param_value[random_indices]

    # calculate the fit with the randomly sampled data points and perturbed
    # known parameters
    fitting_results = easy_fit(x_data_resampled, y_data_resampled,
        model_function, known_params_perturbed, initial_guess,
        y_err_std=y_err_std_resampled, only_positive=only_positive)

    # occasionally the scipy curve fit could fail if it doesn't find the
    # best fit in the required number of steps -> skip such cases
    if fitting_results.success:
        return fitting_results
    return None
