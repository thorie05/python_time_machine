from PySide6.QtWidgets import QPushButton, QSizePolicy
from gui.ui_style import ui_style


class StandardButton(QPushButton):
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
