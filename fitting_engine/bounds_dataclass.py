from dataclasses import dataclass
from typing import Tuple



@dataclass(frozen=True)
class Bounds:
    """
    Contains information about meaningful bounds for all parameters.
    """

    order: Tuple[float, float] = (0.0, 5.0)
    order_std: Tuple[float, float] = (0.0, 1.0)
    f : Tuple[float, float] = (1e-6, 1.0)
    f_std : Tuple[float, float] = (0.0, 1e-4)
    sigma_phi : Tuple[float, float] = (1e-6, 100.0)
    sigma_phi_std : Tuple[float, float] = (0.0, 10.0)
    mu : Tuple[float, float] = (1e-6, 100.0)
    mu_std : Tuple[float, float] = (0.0, 10.0)
