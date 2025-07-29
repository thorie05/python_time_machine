import numpy as np
from . import models
from .full_fit import full_fit

class Calibrator:
    """Class that computes sigma-phi and mu from given calibration data.

    It lazily recalculates sigma-phi and mu when any of the relevant
    parameters or input data changes. Lazily means that the current results are
    marked as dirty and only actually recalculated when accessed. This is
    behavior is achieved with the help of Python's @property syntax.

    Attributes:
        order (float): The order of the model function to be used.
        order_std (float): The standard deviation of the uncertain order.
        sigma_phi (float): The computed sigma-phi value.
        sigma_phi_std (float): The computed standard deviation of sigma-phi.
        mu (float): The computed mu value.
        mu_std (float): The computed standard deviation of mu.
        samples (dict(std: list(float))): Samples of the posterior distribution
            for each free parameter.
        fit_quality (str): String determining the quality of the fit result.
        verbose (bool): Bool flag controling console output.
    """

    def __init__(self, order, order_std, fit_quality="medium", verbose=False):
        """
        Args:
            order (float): The order of the model function to be used.
            order_std (float): The standard deviation of the uncertain order.
            fit_quality (str, optional): Optional string affecting fit quality.
            verbose (bool, optional): Optional flag controling console output.
        """

        # hardcoded sigma_phi and mu bounds
        self.sigma_phi_bounds = (0, 10)
        self.mu_bounds = (0, 10)

        # verbose flag
        self.verbose = verbose

        # shows whether the current results are up to data or "dirty", meaning
        # they need to be recalculated when a results are accessed
        self._dirty = True

        # known parameters
        self._order = order
        self._order_std = order_std
        self._fit_quality = fit_quality

        # calibration input datasets
        self._t_exposure_list = []
        self._x_data_list = []
        self._y_data_list = []
        self._y_err_std_list = []

        # final calibration results
        self._sigma_phi = None
        self._sigma_phi_std = None
        self._mu = None
        self._mu_std = None
        self._samples = None

    @property
    def fit_quality(self):
        """
        Returns:
            str: The fit quality used for the bayesian fit.
        """

        return self._fit_quality

    @fit_quality.setter
    def fit_quality(self, value):
        """Sets the fit quality and lazily recalculates.

        Args:
            value (str): The new fit quality, 'low', 'medium', or 'high'.
        """

        self._fit_quality = value
        self._dirty = True

    @property
    def order(self):
        """
        Returns:
            float: The order of the model function.
        """

        return self._order

    @order.setter
    def order(self, value):
        """Sets the order parameter and lazily recalculates.

        Args:
            value (float): The new order parameter.
        """

        self._order = value
        self._dirty = True

    @property
    def order_std(self):
        """
        Returns:
            float: The standard deviation of order.
        """

        return self._order_std

    @order_std.setter
    def order_std(self, value):
        """Sets the standard deviation of order and lazily recalculates.

        Args:
            value (float): The new standard deviation of order.
        """

        self._order_std = value
        self._dirty = True

    @property
    def sigma_phi(self):
        """
        Returns:
            float: The computed sigma-phi parameter.
        """

        # only recalculate if any of the input parameters has changed
        if self._dirty:
            self._recalculate()
        return self._sigma_phi

    @property
    def sigma_phi_std(self):
        """
        Returns:
            float: The computed standard deviation of sigma-phi.
        """

        # only recalculate if any of the input parameters has changed
        if self._dirty:
            self._recalculate()
        return self._sigma_phi_std

    @property
    def mu(self):
        """
        Returns:
            float: The computed mu parameter.
        """

        # only recalculate if any of the input parameters has changed
        if self._dirty:
            self._recalculate()
        return self._mu

    @property
    def mu_std(self):
        """
        Returns:
            float: The computed standard deviation of mu.
        """

        # only recalculate if any of the input parameters has changed
        if self._dirty:
            self._recalculate()
        return self._mu_std

    @property
    def samples(self):
        """
        Returns:
            dict(str: numpy.ndarray(float)): The posterior samples for sigma-phi
                and mu.
        """

        # only recalculate if any of the input parameters has changed
        if self._dirty:
            self._recalculate()
        return self._samples

    def add_calibration(self, t_exposure, x_data, y_data, y_err_std):
        """Adds new calibration data and lazily recalculates.

        Args:
            t_exposure (float): Exposure time.
            x_data (list or numpy.ndarray: The x-data of the calibration data
                points.
            y_data (list or numpy.ndarray): The y-data of the calibration data
                points.
            y_err_std (list or numpy.ndarray): The standard deviation of the
                y-values.
        """

        self._t_exposure_list.append(t_exposure)
        self._x_data_list.append(x_data)
        self._y_data_list.append(y_data)
        self._y_err_std_list.append(y_err_std)

        self._dirty = True

    def erase_calibration(self, index):
        """Removes calibration data at the given index and lazily recalculates.

        Args:
            index (int): Index of the calibration dataset to remove.
        """

        del self._t_exposure_list[index]
        del self._x_data_list[index]
        del self._y_data_list[index]
        del self._y_err_std_list[index]

        self._dirty = True

    def clear_calibrations(self):
        """Clears all calibration datasets."""

        self._t_exposure_list.clear()
        self._x_data_list.clear()
        self._y_data_list.clear()
        self._y_err_std_list.clear()
        self._dirty = True

    def _recalculate(self):
        """Recalculates the sigma-phi and mu values."""

        # after recalculation all values are up-to-date again
        self._dirty = False

        # ensure that the calibration datasets are not empty
        if not self._x_data_list:
            self._sigma_phi = None
            self._sigma_phi_std = None
            self._mu = None
            self._mu_std = None
            self._samples = None
            return

        # combine individual calibration samples into one large dataset
        x_data_combined = np.concatenate(self._x_data_list)
        y_data_combined = np.concatenate(self._y_data_list)
        y_err_std_combined = np.concatenate(self._y_err_std_list)

        # each datapoint gets an individual t_exposure value for the global fit
        t_exposure_combined = np.concatenate(
            [np.full(len(arr), t_exposure) for arr, t_exposure in \
            zip(self._x_data_list, self._t_exposure_list)])

        # order is a scalar that is constant for all datapoints, t_exposure_1 
        # can differ between datapoints because multiple calibration datasets
        # can be used
        known_params = {"order": self._order,
            "t_exposure_1": t_exposure_combined}
        known_params_err_std = {"order": self._order_std}
        bounds = {"sigma_phi": self.sigma_phi_bounds, "mu": self.mu_bounds}

        # get the best fit values by fitting through the global datasets with
        # individual point values for the exposure time
        # this is more accurate than averaging the results of independent
        # calibration samples or applying a linear fit through the exposure
        # response curve since all available information is considered at once
        fit_result = full_fit(x_data_combined, y_data_combined,
            y_err_std_combined, models.expo, known_params,
            known_params_err_std, bounds=bounds, quality=self._fit_quality,
            only_positive=True, verbose=self.verbose)

        self._sigma_phi = fit_result.best_fit["sigma_phi"]
        self._sigma_phi_std = fit_result.robust_std["sigma_phi"]
        self._mu = fit_result.best_fit["mu"]
        self._mu_std = fit_result.robust_std["mu"]
        self._samples = fit_result.samples
