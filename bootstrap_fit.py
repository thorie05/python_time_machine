from joblib import Parallel, delayed
from easy_fit import easy_fit
import numpy as np


def bootstrap_fit(n, x_data, y_data, model_function, known_params,
    initial_guess, y_err_sigma=None, known_params_err_sigma=None, seed=None):
    """A function that calculates the best fit and standard deviations for the
    given parameters. 

    Takes in an integer n, an array of x- and y-values, the model function
    to use, a dict of known parameters with their respective values, an
    initial guess dict containing the unknown parameters with their respective
    initial guesses and finally an optional array containting the y-errors and
    an optional dict with the errors of the known parameters and an optional
    seed for the random number generator. It returns a dict containing tuples of
    the best numerical values and the 95% confidence intervals for the unknown
    parameters that minimize the squared error of the given model function
    fitted through the datapoints. The function makes use of the bootstrap
    method, so it internally calls the easy fit function n times, making it
    quite time-consuming, even though it works on all cores in parallel. The
    results for the fitted parameters are slightly more accurate than the
    results obtained by only using the easy fit function, but only if n is
    sufficiently large enough. n is recommended to be at least 1000, 10000 or
    even more would be best. The result for each parameter is obtained by taking
    the median of the histogram of the results of all bootstrap iterations.

    Args:
        n (int): Number of times the data gets resampled and perturbed.
        x_data (list or numpy.ndarray): The x-values of the datapoints.
        y_data (list or numpy.ndarray): The y-values of the datapoints.
        model_function (callable): The model function to be used for fitting.
        known_params (dict): Dict containing the known parameters and their
            values.
        initial_guess (dict): Dict containing the unknown parameters and the
            initial guess for each.
        y_err_sigma (list or numpy.ndarray, optional): The standard deviation
            of the y-values.
        known_params_err_sigma (dict, optional): The standard deviation of
            each known parameter.
        seed (int, optional): Optional random number generator seed.

    Returns:
        dict: A dict containing tuples of the values and 95% confidence
        intervals of the fitted parameters.
    """

    # convert input data to np arrays if given as lists
    x_data = np.array(x_data)
    y_data = np.array(y_data)
    if y_err_sigma is not None:
        y_err_sigma = np.array(y_err_sigma)

    rng = np.random.default_rng(seed)
    # make unique seeds of size n for each worker
    seeds = rng.integers(low=0, high=1e9, size=n)

    parallel_results = Parallel(n_jobs=-1)(delayed(single_bootstrap_iteration)(
        seed_i, x_data, y_data, model_function, known_params, initial_guess,
        y_err_sigma, known_params_err_sigma) for seed_i in seeds)

    # set up dict that will store the result of each fit
    fitting_results_lists = {param_name: [] for param_name \
        in initial_guess.keys()}

    # fill the fitting results dict with the results from the parallel execution
    for parallel_result in parallel_results:
        if parallel_result is None:
            continue
        for param_name, value in parallel_result.items():
            fitting_results_lists[param_name].append(value)

    # calculate the median and robust standard deviation for each parameter
    results = {}
    for param_name, values in fitting_results_lists.items():
        values = np.array(values)

        # report lower and upper percentile for 95% confidence range instead of
        # standard deviation since the error could be assymetric
        lower_percentile = np.percentile(values, 2.5)
        upper_percentile = np.percentile(values, 97.5)

        results[param_name] = (np.median(values),
            (lower_percentile, upper_percentile))


    return results, fitting_results_lists


def single_bootstrap_iteration(seed, x_data, y_data, model_function,
    known_params, initial_guess, y_err_sigma=None, known_params_err_sigma=None):
    """
    A function executing an iteration of the bootstrap method.


    Args:
        seed (int): Seed for the random number generator.
        x_data (list or numpy.ndarray): The x-values of the datapoints.
        y_data (list or numpy.ndarray): The y-values of the datapoints.
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

    # randomly choose a new sample of datapoints
    random_indices = rng.choice(len(x_data), size=len(x_data), replace=True)
    x_data_resampled = x_data[random_indices]
    y_data_resampled = y_data[random_indices]

    # if standard deviations for the known parameters are provided perturb
    # each accordingly using the normal distribuation
    known_params_perturbed = known_params.copy()
    if known_params_err_sigma is not None:
        for param_name, value in known_params_perturbed.items():
            known_params_perturbed[param_name] = rng.normal(loc=value,
                scale=known_params_err_sigma[param_name])

    # calculate the fit with the randomly sampled datapoints and perturbed
    # known parameters
    try:
        fitting_results = easy_fit(x_data_resampled, y_data_resampled,
            model_function, known_params_perturbed, initial_guess,
            y_err_sigma=y_err_sigma)
        return fitting_results
    # occasionally the scipy curve fit could fail if it doesnt find the
    # best fit in the required number of steps -> skip such cases
    except RuntimeError:
        return None
