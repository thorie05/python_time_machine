import numpy as np
from inspect import signature
from scipy.optimize import differential_evolution, minimize


def get_initial_guess(x_data, y_data, model_function, known_params, bounds=None,
    y_err_std=None, only_positive=True, num_restarts=5, workers=-1):
    """
    A function that finds an initial guess using global optimization.

    Uses the scipy differential evolution algorithm to globally minimize the
    squared residuals between the model and observed data. The algorithm is run
    the specified number of times to ensure reliable results. Parameters defined
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
        num_restarts (int, optional): Number of differential_evolution runs.
        workers (int, optional): Number of parallel workers.

    Returns:
        dict(str, float): Mapping of free parameter names to their estimated
        initial values.
    """

    # dynamically gets all parameter names of model function discarding x and
    # the optional math variable provided for the pymc fit
    all_param_names = list(signature(model_function).parameters.keys())
    all_param_names.remove("x")
    all_param_names.remove("math")

    # names of the free parameters in the same order as in the model function 
    free_param_names \
        = [name for name in all_param_names if name not in known_params]

    # bounds array has to be in the same order as the free parameters
    if bounds:
        ordered_bounds = [bounds[name] for name in free_param_names]
    else:
        # if no bounds bounds are provided take bounds from -1 million to 1
        # million or 0 to 1 million depending on the only_positive flag
        default_bound = (0, 1_000_000) if only_positive \
            else (-1_000_000, 1_000_000)
        ordered_bounds = [default_bound for _ in free_param_names]

    # residual function that is minimized
    objective = ObjectiveFunction(model_function, x_data, y_data, known_params,
        free_param_names, y_err_std)

    best_result = None
    best_fun = np.inf

    # generate num_restarts different results and take the best
    for seed in range(num_restarts):
        result = differential_evolution(objective, bounds=ordered_bounds,
            strategy='rand1bin', popsize=100, mutation=(0.5, 1),
            maxiter=100_000, polish=False, seed=seed, updating='deferred',
            workers=workers)
        if result.success and result.fun < best_fun:
            best_fun = result.fun
            best_result = result

    if best_result is None:
        raise RuntimeError("Global optimization failed in all restarts.")

    # local optimization at the end to fine-tune the global result
    local_result = minimize(objective, best_result.x, bounds=ordered_bounds,
        method='L-BFGS-B')

    return dict(zip(free_param_names, local_result.x))


class ObjectiveFunction:
    """Objective function class."""

    def __init__(self, model_function, x_data, y_data, known_params,
        free_param_names, y_err_std):
        self.model_function = model_function
        self.x_data = x_data
        self.y_data = y_data
        self.known_params = known_params
        self.free_param_names = free_param_names
        self.y_err_std = y_err_std

    def __call__(self, free_param_values):
        params = self.known_params.copy()
        params.update(zip(self.free_param_names, free_param_values))
        y_model = self.model_function(self.x_data, **params)
        residuals = self.y_data - y_model
        if self.y_err_std is not None:
            residuals /= self.y_err_std
        return np.sum(residuals**2)
