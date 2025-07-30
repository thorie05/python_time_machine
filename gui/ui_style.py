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
    outer_margin: int = 20 # px
    default_width: int = 1200 # px
    default_height: int = 800 # px
    inner_window_spacing: int = 20 # px

@dataclass
class Headline1:
    font_size: int = 24 # px
    font_weight: str = "bold"

@dataclass
class UIStyle:
    table: TableStyle = field(default_factory=TableStyle)
    input: InputStyle = field(default_factory=InputStyle)
    main_window: MainWindow = field(default_factory=MainWindow)
    headline1: Headline1 = field(default_factory=Headline1)

ui_style = UIStyle()
