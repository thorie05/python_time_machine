import numpy as np
from math import isclose

def expo(x, order, sigma_phi, mu, t_expo_1):
    """Mathematical model for a single exposure curve starting from
        saturation.

    Args:
        x (float or numpy.ndarray): The depth(s) in the rock.
        order (float): Order of the mathematical model used.
        sigma_phi (float): Sigma-Phi value, detrapping rate at the surface.
        mu (float): Mu value, light attenuation coefficient in the rock.
        t_expo_1 (float): Exposure time of the rock surface.

    Returns:
        float or numpy.ndarray: The strength of the luminescence signal at
            depth x in the rock.
    """

    # check if order of the model is 1, then use single order kinetics
    if isclose(order, 1.0, rel_tol=1e-9, abs_tol=0.0):
        return np.exp(-sigma_phi * t_expo_1 * np.exp(-mu * x))
    return 0

def expo_buri(x, order, sigma_phi, mu, F, t_expo_1, t_buri_1):
    """Mathematical model for an exposure and burial curve starting from
        saturation.

    Args:
        x (float or numpy.ndarray): The depth(s) in the rock.
        order (float): Order of the mathematical model used.
        sigma_phi (float): Sigma-Phi value, detrapping rate at the surface.
        mu (float): Mu value, light attenuation coefficient in the rock.
        F (float): F = D*(x) / D_0, charge filling rate in the rock, here
            assumend as a constant.
        t_expo_1 (float): Exposure time of the rock surface.
        t_buri_1 (float): Burial time of the rock surface.

    Returns:
        float or numpy.ndarray: The strength of the luminescence signal at
            depth x in the rock.
    """

    # check if order of the model is 1, then use single order kinetics
    if isclose(order, 1.0, rel_tol=1e-9, abs_tol=0.0):
        # recursively calls the single exposure function and uses it as the
        # initial condition
        return 1 - (1 - expo(x, order, sigma_phi, mu, t_expo_1)) \
            * np.exp(-F * t_buri_1)
    return 0
