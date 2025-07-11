from dataclasses import dataclass, field, asdict


@dataclass(frozen=True)
class FitResult:
    """
    Contains all information about the results of a least square fit.

    Can be used for both easy fit (where only best_fit is relevant) and 
    bootstrap fit (where all fields may be populated).

    Args:
        best_fit (dict(str: float)): Dict mapping fit parameter names to
            their best fit values. (Normal best fit for easy fit, median of
            bootstrap samples for bootstrap fit).
        confidence_interval (dict(str: tuple(float, float)), optional): Dict
            mapping fit parameter names to tuples with the lower and upper
            limits of 95% confidence intervals.
        robust_std (dict(str: float), optional): Dict mapping fit parameter
            names to their robust standard deviation calculated from
            percentiles.
        n_missed (int, optional): Number of failed or skipped bootstrap fits.
        bootstrap_samples (dict(str: list(float)), optional): Dict mapping fit
            parameter names to lists of all bootstrap samples.

    Methods:
        as_dict: Returns the FitResult as a plain Python dictionary.
    """

    best_fit: dict = field(default_factory=dict)
    confidence_interval: dict | None = None
    robust_std: dict | None = None
    n_missed: int | None = None
    bootstrap_samples: dict | None = None

    def as_dict(self):
        """Convert the fit result to a dictionary."""

        return asdict(self)
