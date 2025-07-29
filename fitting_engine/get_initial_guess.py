import numpy as np
from inspect import signature
from scipy.optimize import differential_evolution


def get_initial_guess(x_data, y_data, model_function, known_params, bounds=None,
    y_err_std=None, only_positive=True):
    """
    A function that finds an initial guess using global optimization.

    Uses the scipy differential evolution algorithm to globally minimize the
    squared residuals between the model and observed data. Parameters defined
    in 'known_params' are treated as fixed, and the remaining model parameters
    are optimized. The result can be used as an initial guess for the
    bootstrap_fit or easy_fit functions.

    Args:
        x_data (numpy.ndarray): The x-values of the data points.
        y_data (numpy.ndarray): The y-values of the data points.
        model_function (callable): The model function to be used for fitting.
        known_params (dict(str: float or numpy.ndarray)): Dict mapping the known
            parameter names to their known values. If an array is passed it
            has to have the same length as the number of data points.
        bounds (dict(str, Tuple(float, float)), optional): Optional bounds for
            free parameters. If not provided, bounds of (0, 1e6) are used if
            'only_positive' is True, otherwise (-1e6, 1e6).
        y_err_std (numpy.ndarray, optional): Optional standard deviation of the
            y-values.
        only_positive (bool, optional): Optional flag that controls if the fit
            parameters are allowed to be only positive.

    Returns:
        dict(str, float): Mapping of free parameter names to their estimated
        initial values.
    """

    # dynamically gets all parameter names of model function discarding x and
    # the optional math variable provided for the pymc fit
    all_param_names = list(signature(model_function).parameters.keys())
    all_param_names.remove("x")
    all_param_names.remove("math")

    # determine the free paramters
    free_param_names \
        = [name for name in all_param_names if name not in known_params]

    if bounds:
        # construct bounds list in order of free parameters
        ordered_bounds = [bounds[name] for name in free_param_names]
    else:
        # if no bounds provided use either (-1e6, 1e6) or (0, 1e6) for all
        # parameters
        single_bounds = (0, 1_000_000) if only_positive \
            else (-1_000_000, 1_000_000)
        ordered_bounds = [single_bounds for _ in free_param_names]

    # objective function for differntial evolution
    def objective(free_param_values):
        params = known_params.copy()
        params.update(zip(free_param_names, free_param_values))
        y_model = model_function(x_data, **params)
        residuals = y_data - y_model
        if y_err_std is not None:
            residuals /= y_err_std
        return np.sum(residuals**2)

    # global optimization using differential evolution
    de_result = differential_evolution(objective, ordered_bounds,
        strategy='rand1bin', popsize=30, mutation=(0.5, 1), maxiter=10_000,
        polish=True)

    return dict(zip(free_param_names, de_result.x))
