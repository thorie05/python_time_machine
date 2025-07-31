from PySide6.QtWidgets import QProgressBar
from PySide6.QtCore import Qt
from gui.ui_style import ui_style


class StandardProgressBar(QProgressBar):
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