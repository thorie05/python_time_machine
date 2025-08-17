from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QWidget,
    QVBoxLayout,
)

from .style_config import style_tokens


class Button(QPushButton):
    """Button wrapper widget for custom styling."""

    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("Button")

        self.setMinimumHeight(20)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)


class ComboBox(QWidget):
    """ComboBox wrapper widget for custom styling."""

    def __init__(self, label_text, options):
        super().__init__()
        self.setObjectName("ComboBox")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self.label = QLabel(label_text)
        self.combo_box = QComboBox()
        self.combo_box.addItems(options)

        layout.addWidget(self.label)
        layout.addWidget(self.combo_box)

    def get_text(self):
        """Returns the selected text."""

        return self.combo_box.currentText()


class Headline(QLabel):
    """Custom Headline widget."""

    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("Headline")

        self.setContentsMargins(5, 0, 0, 0)
        self.setAlignment(Qt.AlignLeft)


class MessageBoxFitCrash(QMessageBox):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle("Error")
        self.setText("Fit crashed. This should not happen. Could be caused "
            "by bad input data or bad input parameters.\n\nFull Error Message:")

        # create a scrollable text area for the traceback message
        text_edit = QTextEdit()
        text_edit.setPlainText(message)
        text_edit.setReadOnly(True)
        text_edit.setMinimumSize(400, 200)
        text_edit.setMaximumSize(800, 400)
        self.layout().addWidget(text_edit, 1, 0, 1, self.layout().columnCount())


class ProgressBar(QProgressBar):
    """ProgressBar wrapper widget for custom styling."""

    def __init__(self):
        super().__init__()
        self.setObjectName("ProgressBar")

        self.setTextVisible(False)
        self.setRange(0, 0)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(style_tokens.progress_bar.height)
