from . import models
from .fitcore import (
    bayesian_fit,
    easy_fit,
    fit_quality_settings,
    get_initial_guess
)
from .get_event_ages import get_event_ages
from .param_bounds import param_bounds


class FittingEngine():
    """
    A wrapper class to expose all fitting functionality.

    This class provides a unified interface for all fitting functionality,
    combining general-purpose fitting tools from fitcore with OSL-specific
    functions that sit directly in fitting_engine.

    Attributes:
        models (module): Reference to the models module, that provides the
            mathematical model functions used for fitting. Use as:
            engine.models.model_name(...).
        fit_quality_settings (FitQualitySettings): An instance of
            FitQualitySettings for easy access.
        param_bounds (ParamBounds): An instance of ParamBounds for easy access.
        verbose (bool): Bool flag controling console output.

    Methods:
        get_initial_guess
        easy_fit
        bootstrap_fit
        bayesian_fit
        full_fit
        get_event_ages
    """

    def __init__(self, verbose=False):
        self.models = models
        self.fit_quality_settings = fit_quality_settings
        self.param_bounds = param_bounds
        self.verbose = verbose

    def get_initial_guess(self, x_data, y_data, model_function, known_params,
        bounds=None, y_err_std=None, only_positive=True, num_restarts=5,
        workers=-1):
        """Wrapper method for get_initial_guess."""
        return get_initial_guess(x_data, y_data, model_function, known_params,
            bounds=bounds, y_err_std=y_err_std, only_positive=only_positive,
            num_restarts=num_restarts, workers=workers)

    def easy_fit(self, x_data, y_data, model_function, known_params,
        initial_guess, y_err_std=None, only_positive=False):
        """Wrapper method for easy_fit."""

        return easy_fit(x_data, y_data, model_function, known_params,
            initial_guess, y_err_std=y_err_std, only_positive=only_positive)

    def bayesian_fit(self, draws, tune, x_data, y_data, y_err_std,
        model_function, initial_guess, free_params_bounds,
        known_params_distribution, n_walkers=None, seed=None,
        only_positive=False):

        return bayesian_fit(draws, tune, x_data, y_data, y_err_std,
            model_function, initial_guess, free_params_bounds,
            known_params_distribution, n_walkers=n_walkers, seed=seed,
            verbose=self.verbose, only_positive=only_positive)

    def get_event_ages(self, param_names, posterior_samples):
        """Wrapper method for get_event_ages."""

        return get_event_ages(param_names, posterior_samples)
