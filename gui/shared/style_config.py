from dataclasses import asdict, dataclass, field, fields
from typing import List


@dataclass(frozen=True)
class ParamNamesUnicode:
    """Holds unicode names of fit and result parameters."""

    order: str = "order"
    f: str = "F = Ḋ / D₀"
    sigma_phi: str \
        = "<span style='text-decoration: overline;'>σφ</span><sub>0</sub>"
    mu: str = "μ"
    t_exposure_1: str = "t<sub>exposure,1</sub>"
    t_burial_1: str = "t<sub>burial,1</sub>" 
    t_exposure_2: str = "t<sub>exposure,2</sub>" 
    t_burial_2: str = "t<sub>burial,2</sub>"

    def asdict(self):
        return asdict(self)


@dataclass(frozen=True)
class Colors:
    WHITE: str = "#ffffff"
    BLACK: str = "#000000"

    GRAY1: str = "#c0c0c0"
    GRAY2: str = "#e0e0e0"
    GRAY3: str = "#f0f0f0"
    GRAY4: str = "#f8f8f8"

    PLT_DEFAULT_BLUE: str = "#1f77b4"
    PLT_DEFAULT_ORANGE: str = "#ff7f0e"
    PLT_DEFAULT_GREEN: str = "#2ca02c"
    PLT_DEFAULT_RED: str = "#d62728"
    PLT_DEFAULT_PURPLE: str = "#9467bd"
    PLT_DEFAULT_BROWN: str = "#8c564b"
    PLT_DEFAULT_PINK: str = "#e377c2"
    PLT_DEFAULT_GRAY: str = "#7f7f7f"
    PLT_DEFAULT_OLIVE: str = "#bcbd22"
    PLT_DEFAULT_CYAN: str = "#17becf"

colors = Colors()


@dataclass
class Button:
    background_color: str = colors.GRAY3
    background_color_hover: str = colors.GRAY2
    background_color_pressed: str = colors.GRAY1
    border_color: str = colors.GRAY1
    border_width: int = 1 # px
    horizontal_padding: int = 6 # px
    vertical_padding: int = 6 # px


@dataclass
class ComboBox:
    background_color: str = colors.WHITE
    selection_color: str = colors.BLACK


@dataclass
class CalibrationWindow:
    window_title: str = "Python Time Machine"
    background_color: str = colors.WHITE
    outer_margin: int = 30 # px
    outer_margin_lower: int = 0 # px
    default_width: int = 1125 # px
    default_height: int = 750 # px
    inner_window_spacing: int = 10 # px
    top_row_spacing: int = 20 # px
    button_column_top_margin: int = 50 # px
    button_column_spacing: int = 16 # px


@dataclass
class Headline:
    font_size: int = 20 # px
    font_weight: str = "bold"


@dataclass
class HistogramWindow:
    window_title: str = "Histogram"
    background_color: str = colors.WHITE


@dataclass
class MainWindow:
    window_title: str = "Python Time Machine"
    background_color: str = colors.WHITE
    outer_margin: int = 30 # px
    outer_margin_lower: int = 0 # px
    default_width: int = 1200 # px
    default_height: int = 800 # px
    inner_window_spacing: int = 10 # px
    top_row_spacing: int = 20 # px
    button_column_top_margin: int = 50 # px
    button_column_spacing: int = 16 # px


@dataclass
class Plot:
    minimum_height: int = 500 # px
    minimum_width: int = 600 # px
    single_scatter_color: str = colors.PLT_DEFAULT_BLUE
    single_plot_color: str = colors.PLT_DEFAULT_ORANGE
    histogram_color: str = colors.PLT_DEFAULT_BLUE


    color_cycle: List[str] = field(default_factory=lambda: [
        colors.PLT_DEFAULT_BLUE,
        colors.PLT_DEFAULT_ORANGE,
        colors.PLT_DEFAULT_GREEN,
        colors.PLT_DEFAULT_RED,
        colors.PLT_DEFAULT_PURPLE,
        colors.PLT_DEFAULT_BROWN,
        colors.PLT_DEFAULT_PINK,
        colors.PLT_DEFAULT_GRAY,
        colors.PLT_DEFAULT_OLIVE,
        colors.PLT_DEFAULT_CYAN,
    ])


@dataclass
class ProgressBar:
    # border
    border_color: str = colors.GRAY1
    border_width: int = 1  # px
    border_radius: int = 0  # px

    background_color: str = colors.GRAY4
    chunk_color: str = colors.PLT_DEFAULT_BLUE
    chunk_radius: int = 0  # px
    height: int = 5 # px


@dataclass
class Table:
    border_color: str = colors.GRAY1
    border_width: int = 1 # px
    cell_padding: int = 4 # px

    # input cell
    input_background_color: str = colors.WHITE
    input_selection_background_color: str = "#a0c0e0"
    input_selection_border_color: str = "#8080ff"

    # other cell types
    header_background_color: str = colors.GRAY3
    index_background_color: str = colors.GRAY4
    content_background_color: str = colors.WHITE


@dataclass
class StyleTokens:
    """Holds different dataclasses with style tokens."""

    button: Button = field(default_factory=Button)
    calibration_window: CalibrationWindow \
        = field(default_factory=CalibrationWindow)
    combo_box: ComboBox = field(default_factory=ComboBox)
    headline: Headline = field(default_factory=Headline)
    histogram_window: HistogramWindow = field(default_factory=HistogramWindow)
    main_window: MainWindow = field(default_factory=MainWindow)
    plot: Plot = field(default_factory=Plot)
    progress_bar: ProgressBar = field(default_factory=ProgressBar)
    table: Table = field(default_factory=Table)

    def __iter__(self):
        for f in fields(self):
            yield getattr(self, f.name)


param_names_unicode = ParamNamesUnicode()
style_tokens = StyleTokens()

# dict mapping variable names with class name to values
# (e.g. MainWindow.default_width)
# used to fill out the placeholders in style.qss
flat_style_tokens_dict = {}
for outer in fields(style_tokens):
    inst = getattr(style_tokens, outer.name)
    cls_name = type(inst).__name__
    for inner in fields(inst):
        flat_style_tokens_dict[f"{cls_name}.{inner.name}"] \
            = getattr(inst, inner.name)
