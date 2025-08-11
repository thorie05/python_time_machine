from .get_initial_guess import get_initial_guess
from .easy_fit import easy_fit
from .bootstrap_fit import bootstrap_fit
from .bayesian_fit import bayesian_fit
from .full_fit import full_fit
from .get_event_ages import get_event_ages
from .calibrator import Calibrator
from .fit_quality_settings import fit_quality_settings
from . import models


class FittingEngine:
    """
    Wrapper class for all fitting functionality.

    This class exposes the most relevant fitting-related functions as methods
    of a single object. It also provides access to a Calibrator instance, which
    must be manually initialized using init_calibrator(...).

    Attributes:
        calibrator (Calibrator or None): Calibrator instance. Initialize with
            init_calibrator(...) before use.
        models (module): Reference to the models module, which provides the
            mathematical model functions used for fitting. Use as:
            engine.models.model_name(...).
        verbose (bool): Flag controling console output.

    Methods:
        init_calibrator
        easy_fit
        bootstrap_fit
        bayesian_fit
        full_fit
    """

    def __init__(self, verbose=False):
        self.calibrator = None # not initialized yet
        self.models = models
        self.fit_quality_settings = fit_quality_settings
        self.verbose = verbose

    def init_calibrator(self, order, order_std,
        fit_quality=fit_quality_settings.medium, verbose=False):
        """Initialize the internal calibrator instance."""
        self.calibrator = Calibrator(order, order_std, fit_quality=fit_quality,
            verbose=verbose)

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

    def bootstrap_fit(self, n, x_data, y_data, model_function,
        known_params, initial_guess, y_err_std=None,
        known_params_err_std=None, only_positive=False, seed=None):
        """Wrapper method for bootstrap_fit."""

        return bootstrap_fit(n, x_data, y_data, model_function, known_params,
            initial_guess, y_err_std=y_err_std, 
            known_params_err_std=known_params_err_std,
            only_positive=only_positive, seed=seed)

    def bayesian_fit(self, draws, tune, x_data, y_data, model_function,
        known_params, free_params_priors, y_err_std,
        known_params_err_std=None, only_positive=False, cores=4,
        target_accept=0.95, seed=None):
        """Wrapper method for bayesian_fit."""

        return bayesian_fit(draws, tune, x_data, y_data, model_function,
            known_params, free_params_priors, y_err_std,
            known_params_err_std=known_params_err_std,
            only_positive=only_positive, target_accept=target_accept,
            cores=cores, verbose=self.verbose, seed=seed)

    def full_fit(self, x_data, y_data, y_err_std, model_function, known_params,
        known_params_err_std=None, free_params_priors=None, bounds=None,
        fit_quality=fit_quality_settings.medium, only_positive=False, cores=4,
        seed=None, status_callback=None):
        """Wrapper method for full_fit."""

        return full_fit(x_data, y_data, y_err_std, model_function, known_params,
            known_params_err_std=known_params_err_std,
            free_params_priors=free_params_priors, bounds=bounds,
            fit_quality=fit_quality, only_positive=only_positive, cores=cores,
            verbose=self.verbose, seed=seed, status_callback=status_callback)

    def get_event_ages(self, param_names, posterior_samples):
        """Wrapper method for get_event_ages."""

        return get_event_ages(param_names, posterior_samples)
