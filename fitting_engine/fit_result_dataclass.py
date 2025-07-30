from dataclasses import dataclass


@dataclass(frozen=True)
class FitResult:
    """
    Contains all information about the results of a function fit.

    Is returned by easy fit, bootstrap fit and bayesian fit. For easy fit only
    the success flag and best fit dict are populated. The time_since_events list
    is only calculated in the bayesian fit function.

    Args:
        success (bool): Bool informing whether a particular fit was successful
            or if there occured problem that could make the fitting result
            unreliable.
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
        time_sice_events (list(Tuple(float, Tuple(float, float))), optional):
            List containing event timestamps instead of burial/exposure
            timespans as used in the mathematical model functions. The first
            entry of the list holds the total elapsed time since the first
            exposure, the second one the time since the first burial, etc. Each
            list entry is a tuple containing the total elapsed time since an
            event and another tuple holding the associated confidence interval.
    """

    success: bool | None = None
    best_fit: dict | None = None
    confidence_interval: dict | None = None
    robust_std: dict | None = None
    samples: dict | None = None
    time_since_events: list | None = None
