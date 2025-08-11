from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class StdBounds:
    order: tuple = (0.0, 1.0)
    f: tuple = (0.0, 0.0001)
    sigma_phi: tuple = (0.0, 10.0)
    mu: tuple = (0.0, 10.0)

    def asdict(self):
        return asdict(self)


@dataclass(frozen=True)
class ValBounds:
    order: tuple = (0.0, 5.0)
    f: tuple = (0.000001, 1.0)
    sigma_phi: tuple = (0.000001, 100.0)
    mu: tuple = (0.000001, 100.0)
    t_exposure_1: tuple = (0.0, 1_000_000.0)
    t_burial_1: tuple = (0.0, 1_000_000.0)
    t_exposure_2: tuple = (0.0, 1_000_000.0)
    t_burial_2: tuple = (0.0, 1_000_000.0)

    def asdict(self):
        return asdict(self)


@dataclass(frozen=True)
class ParamBounds:
    std: StdBounds = StdBounds()
    val: ValBounds = ValBounds()


param_bounds = ParamBounds()
