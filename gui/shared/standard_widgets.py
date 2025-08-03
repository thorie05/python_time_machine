from PySide6.QtWidgets import QPushButton, QSizePolicy, QProgressBar, QWidget, \
    QVBoxLayout, QLabel, QComboBox, QLayout
from PySide6.QtCore import Signal, Qt

from .ui_style import ui_style


class ClickableLabel(QLabel):
    doubleClicked = Signal()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self.text().strip() != "":
            self.doubleClicked.emit()


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


class StandardComboBox(QWidget):
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


class StandardHeadline(QLabel):
    def __init__(self, text):
        super().__init__(text)

        self.setContentsMargins(5, 0, 0, 0)
        self.setAlignment(Qt.AlignLeft)
        self.setStyleSheet("font-size: "
            f"{ui_style.standard_headline.font_size}px; "
            f"font-weight: {ui_style.standard_headline.font_weight};")


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
