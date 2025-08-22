from dataclasses import dataclass, field


# FitQualitySettings is only used for full_fit, not for easy_fit, bootstrap_fit
#   and bayesian_fit to provide more versatility.

# draws: Number of MCMC samples.
#   A higher number samples increases the accuracy of the fit results.
# tune: Number of MCMC burn-in samples.
#    Should be large enough to ensure correct results, but a too large number
#    throws away valid samples.
# target_accept: Influences the MCMC step-size.
#    Needs to be large enough so all MCMC chains converge, especially when a
#    model with many fit parameters is used and/or input data is noisy.
# n_bootstrap: Number of bootstrap samples used for Bayesina prior estimation.
# num_restarts: Number of global optimization runs used in get_initial_guess.
#   More restarts increase the probability of finding the global minimum.


@dataclass(frozen=True)
class Low:
    draws = 3_000
    tune = 1_000
    target_accept = 0.9
    n_bootstrap = 1_000
    num_restarts = 1

@dataclass(frozen=True)
class Medium:
    draws = 10_000
    tune = 2_000
    target_accept = 0.95
    n_bootstrap = 2_500
    num_restarts = 3

@dataclass(frozen=True)
class High:
    draws = 20_000
    tune = 4_000
    target_accept = 0.99
    n_bootstrap = 5_000
    num_restarts = 10

@dataclass(frozen=True)
class VeryHigh:
    draws = 100_000
    tune = 10_000
    target_accept = 0.999
    n_bootstrap = 10_000
    num_restarts = 50

@dataclass(frozen=True)
class FitQualitySettings:
    """A dataclass containing settings for different fit quality options."""
    
    low: Low = field(default_factory=Low)
    medium: Medium = field(default_factory=Medium)
    high: High = field(default_factory=High)
    very_high: VeryHigh = field(default_factory=VeryHigh)


fit_quality_settings = FitQualitySettings()
