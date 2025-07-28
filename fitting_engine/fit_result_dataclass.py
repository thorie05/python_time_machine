from dataclasses import dataclass, field, asdict


@dataclass(frozen=True)
class FitResult:
    """
    Contains all information about the results of a function fit.

    Is returned by easy fit, bootstrap fit and bayesian fit. For easy fit only
    the best fit dict is populated.

    Args:
        best_fit (dict(str: float)): Dict mapping fit parameter names to
            their best fit values. (Normal best fit for easy fit, median of
            samples for bootstrap and bayesian fit).
        confidence_interval (dict(str: tuple(float, float)), optional): Dict
            mapping fit parameter names to tuples with the lower and upper
            limits of 95% confidence intervals.
        robust_std (dict(str: float), optional): Dict mapping fit parameter
            names to their robust standard deviation calculated from
            percentiles.
        samples (dict(str: list(float)), optional): Dict mapping fit
            parameter names to lists of all bootstrap samples.

    Methods:
        as_dict: Returns the FitResult as a plain Python dictionary.
    """

    best_fit: dict = field(default_factory=dict)
    confidence_interval: dict | None = None
    robust_std: dict | None = None
    samples: dict | None = None
