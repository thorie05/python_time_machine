from dataclasses import dataclass, field

@dataclass
class TableStyle:
    header_background_color: str = "#f0f0f0"
    index_background_color: str = "#f8f8f8"
    cell_background_color: str = "#ffffff"
    border_color: str = "#c0c0c0;"
    border_width: int = 1 # px
    cell_padding: int = 4 # px

@dataclass
class InputStyle:
    background_color: str = "#ffffff"
    selection_background_color: str = "#a0c0e0"
    border_color: str = "#c0c0c0"
    selection_border_color: str = "#8080ff"
    border_width: int = 1 # px
    padding: int = 4 # px

@dataclass
class MainWindow:
    background_color: str = "#ffffff"
    outer_margin: int = 30 # px
    default_width: int = 1200 # px
    default_height: int = 800 # px
    inner_window_spacing: int = 10 # px

@dataclass
class StandardHeadline:
    font_size: int = 20 # px
    font_weight: str = "bold"

@dataclass
class StandardButton:
    background_color: str = "#f0f0f0"
    background_color_hover: str = "#e0e0e0"
    background_color_pressed: str = "#d0d0d0"
    border_color: str = "#aaaaaa"
    border_width: int = 1 # px
    horizontal_padding: int = 6 # px
    vertical_padding: int = 6 # px

@dataclass
class StandardProgressBar:
    border_color: str = "#b0b0b0"
    border_width: int = 1  # px
    border_radius: int = 0  # px
    background_color: str = "#f0f0f0"
    chunk_color: str = "#1f77b4"  # Matplotlib default blue
    chunk_radius: int = 0  # px

@dataclass
class Plot:
    scatter_color: str = "#1f77b4"
    plot_color: str = "#ff7f0e"
    histogram_color: str = "#1f77b4"

@dataclass
class UIStyle:
    table: TableStyle = field(default_factory=TableStyle)
    input: InputStyle = field(default_factory=InputStyle)
    main_window: MainWindow = field(default_factory=MainWindow)
    standard_headline: StandardHeadline \
        = field(default_factory=StandardHeadline)
    standard_button: StandardButton = field(default_factory=StandardButton)
    standard_progress_bar: StandardProgressBar \
        = field(default_factory=StandardProgressBar)
    plot: Plot = field(default_factory=Plot)


ui_style = UIStyle()
