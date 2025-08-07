from dataclasses import dataclass


@dataclass(frozen=True)
class FitResult:
    """
    Contains all information about the results of a function fit.

    Is returned by easy fit, bootstrap fit and bayesian fit. For easy fit only
    the success flag and best fit dict are populated.

    Args:
        success (bool): Bool informing whether a particular fit was successful
            or if there occured problem that could make the fitting result
            unreliable.
        best_fit (dict(str: float)): Dict mapping fit parameter names to
            their best fit values. (Normal best fit for easy fit, median of
            samples for bootstrap and bayesian fit).
        confidence_interval (dict(str: tuple(float, float))): Dict mapping fit
            parameter names to tuples with the lower and upper limits of 95%
            confidence intervals.
        robust_std (dict(str: float)): Dict mapping fit parameter names to their
            robust standard deviation calculated from percentiles.
        samples (dict(str: list(float))): Dict mapping fit parameter names to
            lists of all bootstrap samples.
    """

    success: bool | None = None
    best_fit: dict | None = None
    confidence_interval: dict | None = None
    robust_std: dict | None = None
    samples: dict | None = None
