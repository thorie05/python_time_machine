import numpy as np
from scipy.optimize import curve_fit
from inspect import signature


def easy_fit(x_data, y_data, model_function, known_params, initial_guess,
    y_err_sigma=None):
    """A function that calculates the best fit for the given parameters. 

    Takes in an array of x- and y-values with y-errors, the model function
    to use, a dict of known parameters with their respective values and an
    initial guess dict containing the unknown parameters with their respective
    initial guesses. It returns a dict with the best numerical values for the
    unknown parameters that minimize the squared error of the given model
    function fitted through the datapoints. The function is called easy fit,
    because it doesn't return any errors, which are calculated in the much more
    time-consuming function bootstrap fit, which also provides slightly more
    accurate fit parameters additionally to the errors.

    Args:
        x_data (list or numpy.ndarray): The x-values of the datapoints.
        y_data (list or numpy.ndarray): The y-values of the datapoints.
        model_function (callable): The model function to be used for fitting.
        known_params (dict): Dict containing the known parameters and their
            values.
        initial_guess (dict): Dict containing the unknown parameters and the
            initial guess for each.
        y_err_sigma (list or numpy.ndarray, optional): The standard deviation
            of the y-values.

    Returns:
        dict: A dict containing the names and values of the fitted parameters.
    """

    # convert input data to np arrays if given as lists
    x_data = np.array(x_data)
    y_data = np.array(y_data)
    if y_err_sigma is not None:
        y_err_sigma = np.array(y_err_sigma)

    # dynamically gets all parameter names of model discarding x
    all_param_names = list(signature(model_function).parameters.keys())[1:]

    # names of the unknown parameters in the same order as in the model function 
    unknown_param_names = [name for name in all_param_names if name in \
        initial_guess.keys()]
    # values of the initial guesses in the same order as in the model function
    initial_guess_array = [initial_guess[name] for name in unknown_param_names]

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

    # best curve fit
    popt, _ = curve_fit(model_wrapper, x_data, y_data, p0=initial_guess_array,
        sigma=y_err_sigma, absolute_sigma=(y_err_sigma is not None),
        bounds=([0] * len(unknown_param_names),
        [np.inf] * len(unknown_param_names)), maxfev=10_000)

    fitted_params = dict(zip(unknown_param_names, popt))

    return fitted_params
