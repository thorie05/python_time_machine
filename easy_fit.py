import numpy as np
from scipy.optimize import curve_fit
from inspect import signature
from fit_result_dataclass import FitResult


def easy_fit(x_data, y_data, model_function, known_params, initial_guess,
    y_err_std=None, only_positive=True):
    """A function that calculates the best fit for the given parameters. 

    Takes in an array of x- and y-values, the model function to use, a dict of
    known parameters with their respective values, an initial guess dict
    containing the unknown parameters with their respective initial guesses and
    finally an optional array containing the y-errors and an optional flag that
    ensures all parameters are positive. It returns a dict with the best
    numerical values for the unknown parameters that minimize the squared error
    of the given model function fitted through the data points. The function is
    called easy fit, because it doesn't return any errors, which are calculated
    in the much more time-consuming bootstrap fit function, which also provides
    slightly more accurate fit parameters additionally to the errors.

    Args:
        x_data (list or numpy.ndarray): The x-values of the data points.
        y_data (list or numpy.ndarray): The y-values of the data points.
        model_function (callable): The model function to be used for fitting.
        known_params (dict(str: float)): Dict mapping the known parameter names
            to their known values.
        initial_guess (dict(str: float)): Dict mapping the unknown parameter
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

    # dynamically gets all parameter names of model discarding x
    all_param_names = list(signature(model_function).parameters.keys())[1:]

    # names of the unknown parameters in the same order as in the model function 
    unknown_param_names = [name for name in all_param_names if name in \
        initial_guess.keys()]

    # values of the initial guesses in the same order as in the model function
    initial_guess_array = [initial_guess[name] for name in unknown_param_names]

    # convert model params and user params to sets to check for equality
    set_initial_guess = set(initial_guess.keys())
    set_known_params = set(known_params.keys())
    set_user_params = set_initial_guess.union(set_known_params)
    set_model_params = set(all_param_names)

    # if they don't match throw an exception
    if set_user_params != set_model_params:
        missing = set_model_params - set_user_params
        extra = set_user_params - set_model_params
        msg = []
        if missing:
            msg.append(f"Missing parameters: {sorted(missing)}")
        if extra:
            msg.append(f"Unexpected parameters: {sorted(extra)}")
        raise ValueError("Mismatch between model function parameters and " \
            + "provided parameters.\n" + "\n".join(msg))

    def model_wrapper(x, *curve_fit_unknowns):
        """
        Wrapper helper function for the model function.

        Takes only the unknown parameters as arguments from the scipy curve
        fitter and fills out the remaining parameters with the fixed values.
        """

        # make a dict with the fixed known parameters and the parameter values
        # given by the scipy curve fitter
        calling_params = {name: value for name, value in known_params.items()
            if name in all_param_names} 
        calling_params.update(zip(unknown_param_names, curve_fit_unknowns))

        # call the actual model function with all parameter values
        return model_function(x, **calling_params)

    # allow only positive fit parameters if flag is true by setting bounds
    if only_positive:
        bounds = ([0] * len(unknown_param_names),
            [np.inf] * len(unknown_param_names))
    else:
        bounds = (-np.inf, np.inf)

    # apply best curve fit
    popt, _ = curve_fit(model_wrapper, x_data, y_data, p0=initial_guess_array,
        sigma=y_err_std, absolute_sigma=(y_err_std is not None),
        bounds=bounds, maxfev=10_000)

    fitted_params = dict(zip(unknown_param_names, popt))

    # check if all fit parameter values are valid
    if np.any(np.isnan(list(fitted_params.values()))):
        raise RuntimeError("Fit failed: NaN values in fitted parameters.")

    fit_result = FitResult(best_fit=fitted_params)

    return fit_result
