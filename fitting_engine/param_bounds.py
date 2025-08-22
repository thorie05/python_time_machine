from dataclasses import dataclass, asdict


# The parameter bounds are unit-specific, as opposed to all other fitting
# functionality. It other doesn't need any units, because the results
# automatically use the same units as the input parameters.


@dataclass(frozen=True)
class StdBounds:
    """
    A dataclass storing the lower and upper bounds for the known standard
    deviations of the input parameters. Only relevant for the gui to prohibit
    inputs that would crash the fit.

    Args:
        order (Tuple(float, float)): Bounds for the standard deviation of order.
        f (Tuple(float, float)): Bounds for the standard deviation of f.
        sigma_phi (Tuple(float, float)): Bounds for the standard deviation of
            sigma_phi.
        mu (Tuple(float, float)): Bounds for the standard deviation of mu.
    """

    order: tuple = (0.0, 1.0)
    f: tuple = (0.0, 0.0001)
    sigma_phi: tuple = (0.0, 10.0)
    mu: tuple = (0.0, 10.0)

    def asdict(self):
        return asdict(self)


@dataclass(frozen=True)
class ValBounds:
    """
    A dataclass storing the lower and upper bounds all model parameters. These
    are not only relevant for the gui but also determine the search space for
    the global initial guess finder.

    Args:
        order (Tuple(float, float)): Bounds for order.
        f (Tuple(float, float)): Bounds for f.
        sigma_phi (Tuple(float, float)): Bounds for sigma_phi.
        mu (Tuple(float, float)): Bounds for mu.
        t_exposure_1 (Tuple(float, float)): Bounds for t_exposure_1.
        t_burial_1 (Tuple(float, float)):  Bounds for t_burial_1.
        t_exposure_2 (Tuple(float, float)): Bounds for t_exposure_2.
        t_burial_2 (Tuple(float, float)): Bounds for to_burial_2.
    """

    order: tuple = (0.0, 5.0)
    f: tuple = (0.000001, 1.0)
    sigma_phi: tuple = (0.000001, 100.0)
    mu: tuple = (0.000001, 100.0)
    t_exposure_1: tuple = (0.01, 200_000.0)
    t_burial_1: tuple = (0.01, 200_000.0)
    t_exposure_2: tuple = (0.01, 200_000.0)
    t_burial_2: tuple = (0.01, 200_000.0)

    def asdict(self):
        return asdict(self)


@dataclass(frozen=True)
class ParamBounds:
    """Stores standard deviation and value bounds."""

    std: StdBounds = StdBounds()
    val: ValBounds = ValBounds()


param_bounds = ParamBounds()
