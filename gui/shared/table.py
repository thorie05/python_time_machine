from PySide6.QtWidgets import (
    QSizePolicy,
    QWidget,
    QLabel,
    QFrame,
    QGridLayout,
    QLineEdit,
    QSpacerItem
)
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


class InvisibleCell(QLabel):
    def __init__(self):
        super().__init__()
        self.setObjectName("InvisibleCell")


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

    def __init__(self, table_layout, ghost_rows=0):
        super().__init__()

        self.table_layout = table_layout
        self.ghost_rows = ghost_rows

        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)

        self.table_frame = QFrame()
        self.table_frame.setObjectName("TableFrame")
        self.table_frame.setFrameShape(QFrame.Box)

        self.frame_layout = QGridLayout(self.table_frame)
        self.frame_layout.addLayout(self.grid, 0, 0)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout = QGridLayout(self)
        self.main_layout.addWidget(self.table_frame, 0, 0)
        self.main_layout.setContentsMargins(5, 0, 5, 0)

        self.update_layout()

    def set_cell_text(self, col, row, text):
        label = self.table_layout[row][col]
        new_text = text if text is not None else ""
        label.setText(new_text)

    def _clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

    def update_layout(self):
        self._clear_grid()

        for r, row in enumerate(self.table_layout):
            for c, cell in enumerate(row):
                self.grid.addWidget(cell, r, c)

        # clear old ghost spacer(s) under the frame
        while self.main_layout.count() > 1:
            self.main_layout.takeAt(1)

        # add invisible ghost space outside the framed grid
        if self.ghost_rows > 0:
            self.main_layout.addItem(
                QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 1, 0
            )

        # distribute space as if there were visible_rows + ghost_rows
        self.main_layout.setRowStretch(0, len(self.table_layout))
        self.main_layout.setRowStretch(1, max(0, self.ghost_rows))
