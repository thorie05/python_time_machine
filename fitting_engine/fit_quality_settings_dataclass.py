from dataclasses import dataclass, field

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
    """Contains settings for different fit quality options."""

    low: Low = field(default_factory=Low)
    medium: Medium = field(default_factory=Medium)
    high: High = field(default_factory=High)
    very_high: VeryHigh = field(default_factory=VeryHigh)


fit_quality_settings = FitQualitySettings()
