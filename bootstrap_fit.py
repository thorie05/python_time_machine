from joblib import Parallel, delayed
from easy_fit import easy_fit
import numpy as np
from fit_result_dataclass import FitResult


def bootstrap_fit(n, x_data, y_data, model_function, known_params,
    initial_guess, y_err_sigma=None, known_params_err_sigma=None,
    only_positive=True, return_samples=False, seed=None):
    """A function that calculates the best fit and standard deviations for the
    given parameters. 

    Takes in an integer n, an array of x- and y-values, the model function
    to use, a dict of known parameters with their respective values, an
    initial guess dict containing the unknown parameters with their respective
    initial guesses and finally an optional array containing the y-errors and
    an optional dict with the errors of the known parameters and an optional
    flag that ensures all parameters are positive, an optional indicating
    whether the full bootstrap lists should be returned and an optional seed
    for the random number generator. It returns a dict containing tuples of the
    best numerical values and the 95% confidence intervals for the unknown
    parameters that minimize the squared error of the given model function
    fitted through the data points. The function makes use of the bootstrap
    method, so it internally calls the easy fit function n times, making it
    quite time-consuming, even though it works on all cores in parallel. The
    results for the fitted parameters are slightly more accurate than the
    results obtained by only using the easy fit function, but only if n is
    sufficiently large enough. n is recommended to be at least 1000, 10000 or
    even more would be best. The result for each parameter is obtained by taking
    the median of the histogram of the results of all bootstrap iterations, the
    principle applies to the confidence intervals.

    Args:
        n (int): Number of times the data gets resampled and perturbed.
        x_data (list or numpy.ndarray): The x-values of the data points.
        y_data (list or numpy.ndarray): The y-values of the data points.
        model_function (callable): The model function to be used for fitting.
        known_params (dict(str: float)): Dict containing the known parameters
            and their values.
        initial_guess (dict(str: float)): Dict containing the unknown parameters
            and the initial guess for each.
        y_err_sigma (list or numpy.ndarray, optional): The standard deviation
            of the y-values.
        known_params_err_sigma (dict(str: float), optional): The standard
            deviation of each known parameter.
        only_positive (bool, optional): Flag that controls if the fit parameters
            are allowed to be only positive.
        return_samples (bool, optional): Flag that controls whether the
            bootstrap sample lists are also returned in the fit result.
        seed (int, optional): Optional random number generator seed.

    Returns:
        FitResult: Dataclass containing all relevant information about a fit.
        See documentation for details.
    """

    # convert input data to np arrays if given as lists
    x_data = np.array(x_data)
    y_data = np.array(y_data)
    if y_err_sigma is not None:
        y_err_sigma = np.array(y_err_sigma)

    rng = np.random.default_rng(seed)
    # make unique seeds of size n for each worker
    seeds = rng.integers(low=0, high=np.iinfo(np.uint64).max, size=n,
        dtype=np.uint64)

    parallel_results = Parallel(n_jobs=-1, batch_size="auto") (
        delayed(single_bootstrap_iteration)(seed_i, x_data, y_data,
        model_function, known_params, initial_guess, y_err_sigma,
        known_params_err_sigma, only_positive=only_positive) \
        for seed_i in seeds)

    # set up dict that will store the result of each fit
    bootstrap_samples = {param_name: [] for param_name in initial_guess.keys()}

    # fill the fitting results dict with the results from the parallel execution
    for parallel_result in parallel_results:
        # if easy fit didn't work or gives a result almost equal to zero skip
        res = parallel_result.best_fit
        if res is None or np.any(np.isclose(list(res.values()), 0, atol=1e-8)):
            continue
        for param_name, value in res.items():
            bootstrap_samples[param_name].append(value)

    best_fit_dict = {}
    confidence_interval_dict = {}
    robust_std_dict = {}

    for param_name, values in bootstrap_samples.items():
        values = np.array(values)

        # if theoretically all bootstrap iterations fail for a parameter return
        # None for every metric
        if len(values) == 0:
            best_fit_dict[param_name] = None
            confidence_interval_dict[param_name] = None
            robust_std_dict[param_name] = None
            continue

        # median instead of mean for fit results as it can be more stable
        best_fit_dict[param_name] = np.median(values)

        # calculate lower and upper percentile for 95% confidence range instead
        # of plain standard deviation since the error can be asymetric
        lower_percentile = np.percentile(values, 2.5)
        upper_percentile = np.percentile(values, 97.5)
        confidence_interval_dict[param_name] = \
            (float(lower_percentile), float(upper_percentile))

        # calculate robust standard deviation calculated from the percentiles
        robust_std_dict[param_name] = float((upper_percentile \
            - lower_percentile) / (2 * 1.96))

    # count how many iterations were skipped
    n_valid_per_param = [len(v) for v in bootstrap_samples.values()]
    n_valid = sum(n_valid_per_param) / len(initial_guess)
    n_missed = int(n - n_valid)

    # only return bootstrap samples if specified
    bootstrap_samples = bootstrap_samples if return_samples else None

    # construct fit result dataclass to be returned
    fit_result = FitResult(best_fit=best_fit_dict, confidence_interval=
        confidence_interval_dict, robust_std=robust_std_dict,
        bootstrap_samples=bootstrap_samples, n_missed=n_missed)

    return fit_result


def single_bootstrap_iteration(seed, x_data, y_data, model_function,
    known_params, initial_guess, y_err_sigma=None, known_params_err_sigma=None,
    only_positive=True):
    """
    A function executing an iteration of the bootstrap method.

    Args:
        seed (int): Seed for the random number generator.
        x_data (list or numpy.ndarray): The x-values of the data points.
        y_data (list or numpy.ndarray): The y-values of the data points.
        model_function (callable): The model function to be used for fitting.
        known_params (dict): Dict containing the known parameters and their
            values.
        initial_guess (dict): Dict containing the unknown parameters and the
            initial guess for each.
        y_err_sigma (list or numpy.ndarray, optional): The standard deviation
            of the y-values.
        known_params_err_sigma (dict, optional): The standard deviation of
            each known parameter.

    Returns:
        dict: A dict containing the fitting results of the easy fit function.
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
    y_err_sigma_resampled = None if y_err_sigma is None \
        else y_err_sigma[random_indices]

    # if standard deviations for the known parameters are provided perturb
    # each accordingly using the normal distribuation
    known_params_perturbed = known_params.copy()
    if known_params_err_sigma is not None:
        for param_name, value in known_params_perturbed.items():
            known_params_perturbed[param_name] = rng.normal(loc=value,
                scale=known_params_err_sigma[param_name])
            # allow only positive parameters in normal perturbation if specified
            if only_positive:
                known_params_perturbed[param_name] = max(0,
                    known_params_perturbed[param_name])

    # calculate the fit with the randomly sampled data points and perturbed
    # known parameters
    try:
        fitting_results = easy_fit(x_data_resampled, y_data_resampled,
            model_function, known_params_perturbed, initial_guess,
            y_err_sigma=y_err_sigma_resampled, only_positive=only_positive)
        return fitting_results
    # occasionally the scipy curve fit could fail if it doesn't find the
    # best fit in the required number of steps -> skip such cases
    except RuntimeError:
        return None
