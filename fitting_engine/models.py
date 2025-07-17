import numpy as np

# All time variables are interpreted as consecutive timespans, not timestamps.
# For example: t_exposure_1 = 1000, t_burial_1 = 100, t_exposure_1 = 10 means:
# Starting from full saturation, followed by 1000 time units of exposure,
# followed by 100 time units of burial, followed by 10 time units of exposure.


def expo(x, order, sigma_phi, mu, t_exposure_1):
    """Mathematical model for a single exposure curve starting from saturation.

    Args:
        x (float or numpy.ndarray): The depth(s) in the rock.
        order (float): Order of the mathematical model used.
        sigma_phi (float): Sigma-Phi value, detrapping rate at the surface.
        mu (float): Mu value, light attenuation coefficient in the rock.
        t_exposure_1 (float): Exposure time of the rock surface.

    Returns:
        float or numpy.ndarray: The strength of the luminescence signal at
            depth x in the rock.
    """

    # check if order of the model is 1 -> single order kinetics
    if np.isclose(order, 1.0, rtol=1e-9, atol=0.0):
        return np.exp(-sigma_phi * t_exposure_1 * np.exp(-mu * x))
    # else general order kinetics
    return ((order - 1) * sigma_phi * t_exposure_1 * np.exp(-mu * x) + 1)**(1 \
        / (1 - order))


def expo_buri(x, order, sigma_phi, mu, f, t_exposure_1, t_burial_1):
    """Mathematical model for an exposure-burial curve starting from saturation.

    Args:
        x (float or numpy.ndarray): The depth(s) in the rock.
        order (float): Order of the mathematical model used.
        sigma_phi (float): Sigma-phi value, detrapping rate at the surface.
        mu (float): Mu value, light attenuation coefficient in the rock.
        f (float): f = D*(x) / D_0, charge filling rate in the rock, here
            assumend as a constant.
        t_exposure_1 (float): Exposure time of the rock surface.
        t_burial_1 (float): Burial time of the rock surface.

    Returns:
        float or numpy.ndarray: The strength of the luminescence signal at
            depth x in the rock.
    """

    # get initial condition for the luminescence profile
    l_initial_condition = expo(x, order, sigma_phi, mu, t_exposure_1)

    # burial works same for single and general order kinetics
    return 1 - (1 - l_initial_condition) * np.exp(-f * t_burial_1)


def expo_buri_expo(x, order, sigma_phi, mu, f, t_exposure_1, t_burial_1,
    t_exposure_2):
    """Mathematical model for an exposure-burial-exposure curve starting from
        saturation.

    Args:
        x (float or numpy.ndarray): The depth(s) in the rock.
        order (float): Order of the mathematical model used.
        sigma_phi (float): Sigma-Phi value, detrapping rate at the surface.
        mu (float): Mu value, light attenuation coefficient in the rock.
        f (float): f = D*(x) / D_0, charge filling rate in the rock, here
            assumend as a constant.
        t_exposure_1 (float): First exposure time of the rock surface.
        t_burial_1 (float): Burial time of the rock surface.
        t_exposure_2 (float): Second exposure time of the rock surface.

    Returns:
        float or numpy.ndarray: The strength of the luminescence signal at
            depth x in the rock.
    """

    # get initial condition for the luminescence profile
    l_initial_condition = expo_buri(x, order, sigma_phi, mu, f, t_exposure_1,
        t_burial_1)

    # check if order of the model is 1 -> single order kinetics
    if np.isclose(order, 1.0, rtol=1e-9, atol=0.0):
        return l_initial_condition * np.exp(-sigma_phi * t_exposure_2 \
            * np.exp(-mu * x))
    # else general order kinetics
    return l_initial_condition * ((order - 1) * sigma_phi * t_exposure_2 \
        * np.exp(-mu * x) + 1)**(1 / (1 - order))
