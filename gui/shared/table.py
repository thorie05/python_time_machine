from PySide6.QtWidgets import QSizePolicy, QWidget, QLabel,QFrame, \
    QGridLayout, QLineEdit
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt


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
            self.setTextInteractionFlags(Qt.NoTextInteraction)
            self.setCursor(Qt.ArrowCursor)
        elif self._on_double_click is not None:
            self.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.setCursor(Qt.IBeamCursor)


class InputCell(QLineEdit):
    def __init__(self, default=0.0, bounds=(0.0, 1_000_000.0)):
        super().__init__(str(default))
        self.setObjectName("InputCell")

        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        validator = QDoubleValidator(bounds[0], bounds[1], 8)
        self.setValidator(validator)

    def get_value(self, default=0.0):
        try:
            return float(self.text())
        except ValueError:
            return default


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
        table_frame.setObjectName("TableFrame")
        table_frame.setFrameShape(QFrame.Box)

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
