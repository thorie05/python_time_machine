from dataclasses import dataclass, asdict, field, fields


@dataclass(frozen=True)
class ParamNamesUnicode:
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


colors = Colors()


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
class MainWindow:
    background_color: str = colors.WHITE
    outer_margin: int = 30 # px
    outer_margin_lower: int = 0 # px
    default_width: int = 1200 # px
    default_height: int = 800 # px
    inner_window_spacing: int = 10 # px


@dataclass
class ComboBox:
    background_color: str = colors.WHITE
    selection_color: str = colors.BLACK


@dataclass
class Headline:
    font_size: int = 20 # px
    font_weight: str = "bold"


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
class ProgressBar:
    border_color: str = colors.GRAY1
    border_width: int = 1  # px
    border_radius: int = 0  # px
    background_color: str = colors.GRAY4
    chunk_color: str = colors.PLT_DEFAULT_BLUE
    chunk_radius: int = 0  # px


@dataclass
class Plot:
    scatter_color: str = colors.PLT_DEFAULT_BLUE
    plot_color: str = colors.PLT_DEFAULT_ORANGE
    histogram_color: str = colors.PLT_DEFAULT_BLUE


@dataclass
class StyleTokens:
    table: Table = field(default_factory=Table)
    main_window: MainWindow = field(default_factory=MainWindow)
    headline: Headline = field(default_factory=Headline)
    button: Button = field(default_factory=Button)
    progress_bar: ProgressBar = field(default_factory=ProgressBar)
    plot: Plot = field(default_factory=Plot)
    combo_box: ComboBox = field(default_factory=ComboBox)

    def __iter__(self):
        for f in fields(self):
            yield getattr(self, f.name)


param_names_unicode = ParamNamesUnicode()
style_tokens = StyleTokens()

# dict mapping names with class name to values (e.g. MainWindow.default_width)
flat_style_tokens_dict = {}
for outer in fields(style_tokens):
    inst = getattr(style_tokens, outer.name)
    cls_name = type(inst).__name__
    for inner in fields(inst):
        flat_style_tokens_dict[f"{cls_name}.{inner.name}"] \
            = getattr(inst, inner.name)
