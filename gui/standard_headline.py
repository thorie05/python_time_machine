from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from gui.ui_style import ui_style


class StandardHeadline(QLabel):
    def __init__(self, text):
        super().__init__(text)

        self.setContentsMargins(5, 0, 0, 0)
        self.setAlignment(Qt.AlignLeft)
        self.setStyleSheet("font-size: "
            f"{ui_style.standard_headline.font_size}px; "
            f"font-weight: {ui_style.standard_headline.font_weight};")
