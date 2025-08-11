from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ParamNamesUnicode:
    order: str = "order"
    f: str = "F = Ḋ / D₀"
    sigma_phi: str = "<span style='text-decoration: overline;'>σφ</span><sub>0</sub>"
    mu: str = "μ"
    t_exposure_1: str = "t<sub>exposure,1</sub>"
    t_burial_1: str = "t<sub>burial,1</sub>" 
    t_exposure_2: str = "t<sub>exposure,2</sub>" 
    t_burial_2: str = "t<sub>burial,2</sub>"

    def asdict(self):
        return asdict(self)


param_names_unicode = ParamNamesUnicode()
