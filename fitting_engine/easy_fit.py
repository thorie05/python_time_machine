import numpy as np
from scipy.optimize import least_squares
from inspect import signature
from .fit_result_dataclass import FitResult

def easy_fit(x_data, y_data, model_function, known_params, initial_guess,
             y_err_std=None, only_positive=True):
    """A function that calculates the best fit for the given parameters. 

    Takes in an array of x- and y-values, the model function to use, a dict of
    known parameters with their respective values (different values for every
    datapoint are allowed), an initial guess dict containing the free parameters
    with their respective initial guesses and finally an optional array
    containing the y-errors and an optional flag that ensures all parameters are
    positive. It returns a dict with the best numerical values for the free
    parameters that minimize the squared error of the given model function
    fitted through the data points. The function is called easy fit, because it
    doesn't return any errors, which are instead calculated in a more
    time-consuming bootstrap fit function, which also provides slightly more
    accurate parameter estimates along with uncertainties.

    Args:
        x_data (list or numpy.ndarray): The x-values of the data points.
        y_data (list or numpy.ndarray): The y-values of the data points.
        model_function (callable): The model function to be used for fitting.
        known_params (dict(str: float or numpy.ndarray)): Dict mapping the known
            parameter names to their known values. The values are allowed to be
            different for each data point.
        initial_guess (dict(str: float)): Dict mapping the free parameter
            names to the initial guess for each.
        y_err_std (list or numpy.ndarray, optional): The standard deviation
            of the y-values.
        only_positive (bool, optional): Flag that controls if the fit parameters
            are allowed to be only positive.

    Returns:
        FitResult: Dataclass, for easy fit only best_fit filled out. See
        documentation for details.
    """

    # convert input data to np arrays if given as lists
    x_data = np.asarray(x_data)
    y_data = np.asarray(y_data)
    if y_err_std is not None:
        y_err_std = np.asarray(y_err_std)

    n_points = len(x_data)

    # dynamically gets all parameter names of model function discarding x
    all_param_names = list(signature(model_function).parameters.keys())[1:]

    # names of the free parameters in the same order as in the model function 
    free_param_names = [name for name in all_param_names if name in \
        initial_guess.keys()]

    # values of the initial guesses in the same order as in the model function
    initial_guess_array = [initial_guess[name] for name in free_param_names]

    # convert model params and user params to sets to check for equality
    set_free_params = set(initial_guess.keys())
    set_known_params = set(known_params.keys())
    set_user_params = set_free_params.union(set_known_params)
    set_all_params = set(all_param_names)

    # if they don't match throw an exception
    if set_user_params != set_all_params:
        missing = set_all_params - set_user_params
        extra = set_user_params - set_all_params
        msg = []
        if missing:
            msg.append(f"Missing parameters: {sorted(missing)}")
        if extra:
            msg.append(f"Unexpected parameters: {sorted(extra)}")
        raise ValueError("Mismatch between model function parameters and " \
            + "provided parameters.\n" + "\n".join(msg))

    # validate known dict contents for shape
    for param_name, value in known_params.items():
        arr = np.atleast_1d(value)
        if arr.ndim != 1:
            raise ValueError(
                f"Known parameter '{param_name}' must be scalar or a 1D array, "
                f"but got shape {arr.shape}."
            )
        if arr.size != 1 and arr.size != n_points:
            raise ValueError(
                f"Known parameter '{param_name}' must be scalar or length "
                f"{n_points}, but got length {arr.size}."
            )

    # custom residuals function for least squares
    def residuals(free_param_values):
        # construct dict with the known parameter values and values for the
        # free parameters as provided by the least square optimizer
        params = known_params.copy()
        params.update(zip(free_param_names, free_param_values))
        y_model = model_function(x_data, **params)

        # calculate residuals for the given free parameter values and the
        # model function
        res = y_data - y_model
        if y_err_std is not None:
            res /= y_err_std
        return res

    # allow only positive fit parameters if flag is true by setting bounds
    if only_positive:
        bounds = ([0] * len(free_param_names),
            [np.inf] * len(free_param_names))
    else:
        bounds = ([-np.inf] * len(free_param_names),
            [np.inf] * len(free_param_names))


    # apply least squares fit with custom residual function
    result = least_squares(residuals, x0=initial_guess_array, bounds=bounds,
        max_nfev=10_000,)

    fitted_params = dict(zip(free_param_names, result.x))

    # check if all fit parameter values are valid
    if np.any(np.isnan(list(fitted_params.values()))):
        raise RuntimeError("Fit failed: NaN values in fitted parameters.")

    return FitResult(best_fit=fitted_params)
