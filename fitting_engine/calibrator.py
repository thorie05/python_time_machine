import numpy as np
from . import models
from .easy_fit import easy_fit
from .bootstrap_fit import bootstrap_fit

class Calibrator:
    """Class that computes sigma-phi and mu from given calibration data.

    The Calibrator class stores n, the number of bootstrap iterations and the
    order parameter of the model function, along with any added calibration
    datasets.It lazily recalculates the dependent results, sigma-phi and
    mu, whenever n, order or the calibration data change. The class uses
    Python's @property syntax to expose attribute access for n and order.
    Internally, the actual data is stored in private variables (with leading
    underscores), while the properties automatically trigger recalculation upon
    any change. This ensures that external code can safely read and update the
    known inputs, while always getting up-to-date results for sigma-phi and mu.

    Attributes:
        n (int): The number of bootstrap iterations.
        order (float): The order of the model function to be used.
        sigma_phi (float): The computed sigma-phi value.
        sigma_phi_std (float): The computed standard deviation of sigma-phi.
        mu (float): The computed mu value.
        mu_std (float): The computed standard deviation of mu.
        bootstrap_samples (dict(std: list(float))): Samples of each bootstrap
            iteration.
    """

    def __init__(self, n, order, initial_guess_sigma_phi=5,
        initial_guess_mu=5):
        """
        Args:
            n (int): The number of bootstrap iterations.
            order (float): The order of the model function to be used.
            initial_guess_sigma_phi (float): The initial guess for sigma-phi.
            initial_guess_mu (float): The initial guess for mu.
        """

        self._n = n
        self._dirty = True

        # known parameter
        self._order = order

        # calibration input datasets
        self._t_exposure_list = []
        self._x_data_list = []
        self._y_data_list = []
        self._y_err_std_list = []

        # initial guesses
        self.initial_guess_sigma_phi = initial_guess_sigma_phi
        self.initial_guess_mu = initial_guess_mu

        # final calibration results
        self._sigma_phi = None
        self._sigma_phi_std = None
        self._mu = None
        self._mu_std = None
        self._bootstrap_samples = None

    @property
    def n(self):
        """
        Returns:
            int: The number of bootstrap iterations.
        """

        return self._n

    @n.setter
    def n(self, value):
        """Sets n and lazily recalculates the results.

        Args:
            value (int): The new number of bootstrap iterations.
        """

        self._n = value
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
        """Sets the order parameter and lazily recalculates the results.

        Args:
            value (float): The new order parameter.
        """

        self._order = value
        self._dirty = True

    @property
    def sigma_phi(self):
        """
        Returns:
            float: The computed sigma-phi parameter.
        """

        self._recalculate()
        return self._sigma_phi

    @property
    def sigma_phi_std(self):
        """
        Returns:
            float: The computed standard deviation of sigma-phi.
        """

        self._recalculate()
        return self._sigma_phi_std

    @property
    def mu(self):
        """
        Returns:
            float: The computed mu parameter.
        """

        self._recalculate()
        return self._mu

    @property
    def mu_std(self):
        """
        Returns:
            float: The computed standard deviation of mu.
        """

        self._recalculate()
        return self._mu_std

    @property
    def bootstrap_samples(self):
        """
        Returns:
            dict(str: list(float)): The bootstrap samples for sigma-phi and mu.
        """

        self._recalculate()
        return self._bootstrap_samples

    def add_calibration(self, t_exposure, x_data, y_data, y_err_std=None):
        """Adds new calibration data and lazily recalculates the results.

        Args:
            t_exposure (float): Exposure time.
            x_data (list or numpy.ndarray: The x-data of the calibration data
                points.
            y_data (list or numpy.ndarray): The y-data of the calibration data
                points.
            y_err_std (list or numpy.ndarray, optional): The standard deviation
                of the y-values.
        """

        self._t_exposure_list.append(t_exposure)
        self._x_data_list.append(x_data)
        self._y_data_list.append(y_data)
        self._y_err_std_list.append(y_err_std)

        # check that y error standard deviations are either provided for all
        # datapoints or for none, no mixture is allowed
        flags = [val is not None for val in self._y_err_std_list]
        # if there's a mix of True and False, raise error
        if len(set(flags)) > 1:
            raise ValueError("Either all y errors must be None or all must"
                " have values, no mixture allowed.")

        self._dirty = True

    def erase_calibration(self, index):
        """Removes calibration data at the given index and recalculates results.

        Args:
            index (int): Index of the calibration dataset to remove.
        """

        del self._t_exposure_list[index]
        del self._x_data_list[index]
        del self._y_data_list[index]
        del self._y_err_std_list[index]

        self._dirty = True

    def _recalculate(self):
        """Lazily recalculates sigma-phi and mu values."""

        # only do the heavy calculation when something has changed
        if not self._dirty:
            return

        # ensure that the calibration datasets are not empty
        if not self._x_data_list:
            self.sigma_phi = None
            self.sigma_phi_std = None
            self.mu = None
            self.mu_std = None
            return

        # combine individual calibration samples into one large dataset
        x_data_combined = np.concatenate(self._x_data_list)
        y_data_combined = np.concatenate(self._y_data_list)
        y_err_std_combined = None
        if self._y_err_std_list[0] is not None:
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

        initial_guess = {"sigma_phi": self.initial_guess_sigma_phi,
            "mu": self.initial_guess_mu}

        # get the best fit values by fitting through the global datasets with
        # individual point values for the exposure time
        # more accurate than averaging the results of independent calibration
        # samples and applying a linear fit through the exposure response curve
        fit_result = bootstrap_fit(self._n, x_data_combined, y_data_combined,
            models.expo, known_params, initial_guess=initial_guess,
            y_err_std=y_err_std_combined, only_positive=True,
            return_samples=True)

        self._sigma_phi = fit_result.best_fit["sigma_phi"]
        self._sigma_phi_std = fit_result.robust_std["sigma_phi"]
        self._mu = fit_result.best_fit["mu"]
        self._mu_std = fit_result.robust_std["mu"]
        self._bootstrap_samples = fit_result.bootstrap_samples

        # all data is clean and up-to-date again
        self._dirty = False
