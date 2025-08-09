from PySide6.QtWidgets import QPushButton, QSizePolicy, QProgressBar, QWidget, \
    QVBoxLayout, QLabel, QComboBox, QLayout, QFrame, QGridLayout
from PySide6.QtCore import Signal, Qt

from .ui_style import ui_style


class Button(QPushButton):
    def __init__(self, text):
        super().__init__(text)

        self.setMinimumHeight(20)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {
                    ui_style.standard_button.background_color
                };
                border: {ui_style.standard_button.border_width}px solid {
                    ui_style.standard_button.border_color
                };
                padding: {
                    ui_style.standard_button.vertical_padding
                }px {
                    ui_style.standard_button.vertical_padding
                }px;
            }}
            QPushButton:hover {{
                background-color: {
                    ui_style.standard_button.background_color_hover
                };
            }}
            QPushButton:pressed {{
                background-color: {
                    ui_style.standard_button.background_color_pressed
                };
            }}
            """
        )


class ComboBox(QWidget):
    def __init__(self, label_text, options):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetFixedSize)

        self.label = QLabel(label_text)
        self.combo_box = QComboBox()
        self.combo_box.addItems(options)

        self.combo_box.setStyleSheet("""
            QComboBox QAbstractItemView {
                selection-color: black;
            }
            """)

        layout.addWidget(self.label)
        layout.addWidget(self.combo_box)

    def get_text(self):
        return self.combo_box.currentText()


class Headline(QLabel):
    def __init__(self, text):
        super().__init__(text)

        self.setContentsMargins(5, 0, 0, 0)
        self.setAlignment(Qt.AlignLeft)
        self.setStyleSheet("font-size: "
            f"{ui_style.standard_headline.font_size}px; "
            f"font-weight: {ui_style.standard_headline.font_weight};")


class ProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTextVisible(False)
        self.setRange(0, 0)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(4)

        self.setStyleSheet(
            f"""
            QProgressBar {{
                border: {ui_style.standard_progress_bar.border_width}px solid 
                    {ui_style.standard_progress_bar.border_color};
                border-radius: 
                    {ui_style.standard_progress_bar.border_radius}px;
                background-color: 
                    {ui_style.standard_progress_bar.background_color};
            }}

            QProgressBar::chunk {{
                background-color: 
                    {ui_style.standard_progress_bar.chunk_color};
                border-radius: 
                    {ui_style.standard_progress_bar.chunk_radius}px;
                margin: 0px;
            }}
            """
        )


class BaseCell(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setObjectName("BaseCell")

        self.setTextFormat(Qt.RichText)
        self.setSizePolicy(QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignVCenter)


class HeaderCell(BaseCell):
    def __init__(self, text=""):
        super().__init__(text)
        self.setObjectName("HeaderCell")


class IndexCell(BaseCell):
    def __init__(self, text=""):
        super().__init__(text)
        self.setObjectName("IndexCell")


class ClickableContentCell(BaseCell):
    def __init__(self, text=""):
        super().__init__(text)
        self.setObjectName("ContentCell")

        self._on_double_click = None

        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._update_cursor()

    def setText(self, text):
        super().setText(text)
        self._update_cursor()

    def connect_double_click(self, func):
        self._on_double_click = func
        self._update_cursor()

    def disconnect_double_click(self):
        self._on_double_click = None
        self._update_cursor()

    def mouseDoubleClickEvent(self, ev):
        if self._on_double_click is not None and ev.button() == Qt.LeftButton:
            self._on_double_click()
            return
        super().mouseDoubleClickEvent(ev)

    def _update_cursor(self):
        if not self.text():
            self.setCursor(Qt.ArrowCursor)  # no text
        elif self._on_double_click is not None:
            self.setCursor(Qt.PointingHandCursor)  # clickable text
        else:
            self.setCursor(Qt.IBeamCursor)  # text but not clickable


class Table(QWidget):
    """Standard table widget."""

    def __init__(self, table_layout):
        super().__init__()

        self.table_layout = table_layout

        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)

        for row_index, row in enumerate(self.table_layout):
            for col_index, cell in enumerate(row):
                self.grid.addWidget(cell, row_index, col_index)

        for row in range(self.grid.rowCount()):
            self.grid.setRowStretch(row, 1)

        for col in range(self.grid.columnCount()):
            self.grid.setColumnStretch(col, 1)

        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Box)
        table_frame.setStyleSheet(
            f"QFrame {{ border: {ui_style.table.border_width}px solid "
            f"{ui_style.table.border_color}; }}"
        )

        frame_layout = QGridLayout(table_frame)
        frame_layout.addLayout(self.grid, 0, 0)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QGridLayout(self)
        main_layout.addWidget(table_frame, 0, 0)
        main_layout.setContentsMargins(5, 0, 5, 0)

    def set_cell_text(self, col, row, text):
        label = self.table_layout[row][col]
        new_text = text if text is not None else ""
        label.setText(new_text)
