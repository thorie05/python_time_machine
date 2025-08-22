import numpy as np

# The fitting functions (easy_fit, bootstrap_fit, bayesian_fit, full_fit) expect
# the model functions to have x, the variable of the mathematical function, as
# the the first argument. Other arguments are treated as parameters that can
# either have known values are be used as fit/free parameters. All functions
# also need to have a math argument where numpy or pymc math can be passed and
# it has work with both math frameworks.

# All time variables are interpreted as consecutive timespans, not event ages.
# For example: t_exposure_1 = 1000, t_burial_1 = 100, t_exposure_2 = 10 means:
# Starting from full saturation, followed by 1000 time units of exposure,
# followed by 100 time units of burial, followed by 10 time units of exposure.
# The elapsed time since an event, e.g. the event age can be most accurately
# calculated from the posterior samples obtianed through the bayesian_fit
# function. This is implemented in get_event_ages.

# The order parameter is subtacted by 1, meaning an order of 0.0 in the code is
# equivalent to the first-order model or an order of 1.2 in the code is
# equivalent to the general-order model with an order of 2.2. This makes the
# implementation easier, because now all parameters (sigma_phi, mu, f and order)
# are always non-negative. Therefore, the only_positive flag is enough for all
# parameters, without making an exception for the order parameter, which
# otherwise would have only allowed values greater than 1. This becomes relevant
# when the known parameters including order are perturbed according to the
# truncated-normal distribution, as in bootstrap_fit or bayesian_fit.

# Avoid having two different formulas for the first- and general-order models
# by treating the first order model as general order model with the specified
# order being very close to 0 and thus practically indistinguishable.
SINGLE_ORDER_VAL = 1e-6


def expo(x, order, sigma_phi, mu, t_exposure_1, math=np):
    """Mathematical model for a single exposure curve starting from saturation.

    Args:
        x (float or numpy.ndarray): The depth(s) in the rock.
        order (float): Order of the mathematical model used.
        sigma_phi (float): Sigma-Phi value, detrapping rate at the surface.
        mu (float): Mu value, light attenuation coefficient in the rock.
        t_exposure_1 (float): Exposure time of the rock surface.
        math (module, optional): Optional variable controling the math used
            math module, with numpy being the default value. This is convenient
            because in bayesian_fit which uses pymc simply pymc.math is passed.

    Returns:
        float or numpy.ndarray: The strength of the luminescence signal at
            depth x in the rock.
    """

    # if order is 0 (single-order) assign the specified single-order value to
    # avoid having to use two distinct formulas
    order = math.maximum(order, SINGLE_ORDER_VAL)

    return (order * sigma_phi * t_exposure_1 * math.exp(-mu * x) + 1) \
        **(-1 / order)


def expo_buri(x, order, sigma_phi, mu, f, t_exposure_1, t_burial_1, math=np):
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
        math (module, optional): Optional variable controling the math used
            math module, with numpy being the default value. This is convenient
            because in bayesian_fit which uses pymc simply pymc.math is passed.

    Returns:
        float or numpy.ndarray: The strength of the luminescence signal at
            depth x in the rock.
    """

    # get initial condition for the luminescence profile
    l_initial_condition = expo(x, order, sigma_phi, mu, t_exposure_1)

    # burial works same for single and general order kinetics
    return 1 - (1 - l_initial_condition) * math.exp(-f * t_burial_1)


def expo_buri_expo(x, order, sigma_phi, mu, f, t_exposure_1, t_burial_1,
    t_exposure_2, math=np):
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
        math (module, optional): Optional variable controling the math used
            math module, with numpy being the default value. This is convenient
            because in bayesian_fit which uses pymc simply pymc.math is passed.

    Returns:
        float or numpy.ndarray: The strength of the luminescence signal at
            depth x in the rock.
    """

    l_initial_condition = expo_buri(x, order, sigma_phi, mu, f, t_exposure_1,
        t_burial_1)

    order = math.maximum(order, SINGLE_ORDER_VAL)

    return l_initial_condition * (order * sigma_phi * t_exposure_2 \
        * math.exp(-mu * x) + 1)**(-1 / order)

def expo_buri_expo_buri(x, order, sigma_phi, mu, f, t_exposure_1, t_burial_1,
    t_exposure_2, t_burial_2, math=np):
    """Mathematical model for an exposure-burial-exposure-burial curve.

    Args:
        x (float or numpy.ndarray): The depth(s) in the rock.
        order (float): Order of the mathematical model used.
        sigma_phi (float): Sigma-phi value, detrapping rate at the surface.
        mu (float): Mu value, light attenuation coefficient in the rock.
        f (float): f = D*(x) / D_0, charge filling rate in the rock, here
            assumend as a constant.
        t_exposure_1 (float): First exposure time of the rock surface.
        t_burial_1 (float): First burial time of the rock surface.
        t_exposure_1 (float): Second exposure time of the rock surface.
        t_burial_1 (float): Second burial time of the rock surface.
        math (module, optional): Optional variable controling the math used
            math module, with numpy being the default value. This is convenient
            because in bayesian_fit which uses pymc simply pymc.math is passed.

    Returns:
        float or numpy.ndarray: The strength of the luminescence signal at
            depth x in the rock.
    """

    l_initial_condition = expo_buri_expo(x, order, sigma_phi, mu, f,
        t_exposure_1, t_burial_1, t_exposure_2)

    return 1 - (1 - l_initial_condition) * math.exp(-f * t_burial_2)
