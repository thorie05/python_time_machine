import numpy as np
from scipy.optimize import least_squares
from inspect import signature
from .fit_result_dataclass import FitResult

def easy_fit(x_data, y_data, model_function, known_params, initial_guess,
             y_err_std=None, only_positive=False):
    """A fast least square fitting function without error estimation.

    A function that takes datapoints and a mathematical model function to
    calculate the least squares best fit of the model through the datapoints. It
    uses scipy's least_square function. Different known parameter values for
    individual data points are allowed, which is useful for fitting multiple
    calibration samples with different exposure times at once.

    Args:
        x_data (numpy.ndarray): The x-values of the data points.
        y_data (numpy.ndarray): The y-values of the data points.
        model_function (callable): The model function to be used for fitting.
        known_params (dict(str: float or numpy.ndarray)): Dict mapping the known
            parameter names to their known values. If an array is passed it
            has to have the same length as the number of data points.
        initial_guess (dict(str: float)): Dict mapping the free parameter
            names to the initial guess for each.
        y_err_std (list or numpy.ndarray, optional): The standard deviation
            of the y-values.
        only_positive (bool, optional): Flag that controls if the fit parameters
            are allowed to be only positive.

    Returns:
        FitResult: Dataclass containing all relevant information about a fit.
            See documentation for details.
    """

    # dynamically gets all parameter names of model function discarding x and
    # the optional math variable provided for the pymc fit
    all_param_names = list(signature(model_function).parameters.keys())
    all_param_names.remove("x")
    all_param_names.remove("math")

    # names of the free parameters in the same order as in the model function 
    free_param_names = [name for name in all_param_names if name in \
        initial_guess.keys()]

    # values of the initial guesses in the same order as in the model function
    initial_guess_array = [initial_guess[name] for name in free_param_names]

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
    try:
        result = least_squares(residuals, x0=initial_guess_array, bounds=bounds,
            max_nfev=10_000,)
        fitted_params = dict(zip(free_param_names, result.x))
    except RuntimeError:
        return FitResult(success=False)

    return FitResult(success=True, best_fit=fitted_params)
