from dataclasses import dataclass
from typing import Tuple



@dataclass(frozen=True)
class Bounds:
    """
    Contains information about meaningful bounds for all parameters.
    """

    order: Tuple[float, float] = (0.0, 5.0)
    order_std: Tuple[float, float] = (0.0, 1.0)
    f : Tuple[float, float] = (0.000001, 1.0)
    f_std : Tuple[float, float] = (0.0, 0.0001)
    sigma_phi : Tuple[float, float] = (0.000001, 100.0)
    sigma_phi_std : Tuple[float, float] = (0.0, 10.0)
    mu : Tuple[float, float] = (0.000001, 100.0)
    mu_std : Tuple[float, float] = (0.0, 10.0)
    t_exposure_1 : Tuple[float, float] = (0.0, 1_000_000.0)
    t_burial_1 : Tuple[float, float] = (0.0, 1_000_000.0)
    t_exposure_2 : Tuple[float, float] = (0.0, 1_000_000.0)
    t_burial_2 : Tuple[float, float] = (0.0, 1_000_000.0)


bounds = Bounds()
