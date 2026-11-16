from dataclasses import dataclass, field


# FitQualitySettings is only used for full_fit, not for easy_fit
#   and bayesian_fit to provide more versatility.

# draws: Number of MCMC sampling steps per walker.
#   A higher number of steps increases the accuracy of the fit results.
# tune: Number of MCMC burn-in steps per walker.
#   Should be large enough to allow the walkers to reach the posterior
#   distribution before collecting samples.
# num_restarts: Number of global optimization runs used in get_initial_guess.
#   More restarts increase the probability of finding the global minimum.


@dataclass(frozen=True)
class Low:
    draws = 5_000
    tune = 1_000
    num_restarts = 1

@dataclass(frozen=True)
class Medium:
    draws = 10_000
    tune = 2_000
    num_restarts = 3

@dataclass(frozen=True)
class High:
    draws = 50_000
    tune = 5_000
    num_restarts = 5

@dataclass(frozen=True)
class VeryHigh:
    draws = 100_000
    tune = 10_000
    num_restarts = 10

@dataclass(frozen=True)
class FitQualitySettings:
    """A dataclass containing settings for different fit quality options."""

    low: Low = field(default_factory=Low)
    medium: Medium = field(default_factory=Medium)
    high: High = field(default_factory=High)
    very_high: VeryHigh = field(default_factory=VeryHigh)


fit_quality_settings = FitQualitySettings()
