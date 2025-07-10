import numpy as np
from easy_fit import easy_fit
from models import expo


class Calibrator:
    def __init__(self, order, f):
        # public
        self.order = order
        self.f = f

        # private
        self._sigma_phi = None
        self._mu = None
        self._sigma_phi_mu_array = []
        self._dirty = True

    def add_calibration_data(self, x_data, y_data, known_t_exp, y_err_sigma=None):
        pass

    def remove_calibration_data(self, index):
        pass
