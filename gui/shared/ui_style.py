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
class MainWindow:
    background_color: str = "#ffffff"
    outer_margin: int = 30 # px
    default_width: int = 1200 # px
    default_height: int = 800 # px
    inner_window_spacing: int = 10 # px

@dataclass
class Plot:
    scatter_color: str = "#1f77b4"
    plot_color: str = "#ff7f0e"
    histogram_color: str = "#1f77b4"

@dataclass
class UIStyle:
    table: TableStyle = field(default_factory=TableStyle)
    main_window: MainWindow = field(default_factory=MainWindow)
    plot: Plot = field(default_factory=Plot)


ui_style = UIStyle()
