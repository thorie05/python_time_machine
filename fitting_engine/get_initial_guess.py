import numpy as np
from inspect import signature
from scipy.optimize import differential_evolution

def get_initial_guess(x_data, y_data, model_function, known_params, bounds,
    y_err_std=None):
    """
    A function that 
    """

    # dynamically gets all parameter names of model function discarding x and
    # the optional math variable provided for the pymc fit
    all_param_names = list(signature(model_function).parameters.keys())
    all_param_names.remove("x")
    all_param_names.remove("math")

    # determine the free paramters
    free_param_names \
        = [name for name in all_param_names if name not in known_params]

    # construct bounds list in order of free parameters
    ordered_bounds = [bounds[name] for name in free_param_names]

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
