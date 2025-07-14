import numpy as np
import models
from easy_fit import easy_fit
from bootstrap_fit import bootstrap_fit

class Calibrator:
    """Class that computes sigma-phi and mu from given calibration data.

    The Calibrator class stores the order and f parameters, along with any added
    calibration datasets. It immediately recalculates the dependent results,
    sigma-phi and mu, whenever the order, f, or the calibration data change. The
    class uses Python's @property syntax to expose attribute access for 'order'
    and 'f'. Internally, the actual data is stored in private variables (with
    leading underscores), while the properties automatically trigger
    recalculation upon any change. This ensures that external code can safely
    read and update the known inputs, while always getting up-to-date results
    for sigma-phi and mu. If order or f are changed, every added calibration
    dataset has to be recalculated. If only a new dataset is added, only the new
    one is recalculated and the result arrays are recombined to give the final
    results for sigma-phi and mu.

    Attributes:
        order (float): The order of the model function to be used.
        f (float): The charge filling rate in the rock.
        sigma_phi (float): The computed sigma-phi value.
        mu (float): The computed mu value.
    """

    def __init__(self, order, f):
        # known parameters, if changed everything has to be recalculated
        self._order = order
        self._f = f

        # calibration input data, if changed only the added dataset has to be
        # fitted and the final results have to be recalculated from the arrays
        self._calibration_t_exposure = []
        self._calibration_x_data = []
        self._calibration_y_data = []
        self._calibration_y_err_std = []

        # computed result arrays
        self._sigma_phi_array = []
        self._mu_array = []
        self._sigma_phi_std_array = []
        self._mu_std_array = []

        # final results computed from the result arrays
        self.sigma_phi = None
        self.mu = None

    def __repr__(self):
        """Returns a string representation of the Calibrator.

        Returns:
            str: Formatted string showing current attributes and results.
        """
        return f"order:     {self.order}\n" \
             + f"f:         {self.f}\n" \
             + f"sigma_phi: {self.sigma_phi}\n" \
             + f"mu:        {self.mu}"

    @property
    def order(self):
        """
        Returns:
            float: The order of the model function.
        """
        return self._order

    @order.setter
    def order(self, value):
        """Sets the order parameter and recalculates the results.

        Args:
            value (float): The new order parameter.
        """
        self._order = value
        self._recalculate(True)
        self._combine_result_arrays()

    @property
    def f(self):
        """
        Returns:
            float: The charge filling rate in the rock.
        """
        return self._f

    @f.setter
    def f(self, value):
        """Sets the f parameter and recalculates the results.

        Args:
            value (float): The new charge filling rate parameter.
        """
        self._f = value
        self._recalculate(True)
        self._combine_result_arrays()

    def add_calibration(self, t_exposure, x_data, y_data, y_err_std=None):
        """Adds new calibration data and recalculates results.

        Args:
            t_exposure (float): Exposure time.
            x_data (array-like): Input X data.
            y_data (array-like): Input Y data.
            y_err_std (array-like, optional): Standard deviation of Y error.
        """
        self._calibration_t_exposure.append(t_exposure)
        self._calibration_x_data.append(x_data)
        self._calibration_y_data.append(y_data)
        self._calibration_y_err_std.append(y_err_std)

        # create matching slots in the result arrays
        self._sigma_phi_array.append(None)
        self._sigma_phi_std_array.append(None)
        self._mu_array.append(None)
        self._mu_std_array.append(None)

        # only the most recently added calibration dataset needs to be fitted
        self._recalculate(False)
        self._combine_result_arrays()

    def erase_calibration(self, index):
        """Removes calibration data at the given index and recalculates results.

        Args:
            index (int): Index of the calibration dataset to remove.
        """

        del self._calibration_t_exposure[index]
        del self._calibration_x_data[index]
        del self._calibration_y_data[index]
        del self._calibration_y_err_std[index]
        del self._sigma_phi_array[index]
        del self._sigma_phi_std_array[index]
        del self._mu_array[index]
        del self._mu_std_array[index]

        # no fitting needed, only the reclculation of sigma-phi and mu from the
        # result arrays
        self._combine_result_arrays()

    def _recalculate(self, full_refit, n=10_000):
        last_index = len(self._calibration_t_exposure) - 1

        # don't recalculate anything if there are no added datasets
        if last_index < 0:
            return

        # only recalulculate last index (newly added) depending on the flag
        start_index = 0 if full_refit else last_index

        # loop through all indices that need to be recalculated and update the
        # result arrays
        for i in range(start_index, last_index + 1):
            # use bootstrap fit to also get the standard deviation
            fit_result = bootstrap_fit(n, self._calibration_x_data[i],
                self._calibration_y_data[i], models.expo,
                {"t_exposure_1": self._calibration_t_exposure[i]},
                {"sigma_phi": 5, "mu": 5},
                y_err_std=self._calibration_y_err_std[i], only_positive=True,
                return_samples=False)

            self._sigma_phi_array[i] = fit_result.best_fit["sigma_phi"]
            self._sigma_phi_std_array[i] = fit_result.robust_std["sigma_phi"]
            self._mu_array[i] = fit_result.best_fit["mu"]
            self._mu_std_array[i] = fit_result.robust_std["mu"]


    def _combine_result_arrays(self):
        pass
