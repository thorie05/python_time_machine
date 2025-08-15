from PySide6.QtWidgets import QPushButton, QSizePolicy, QProgressBar, QWidget, \
    QVBoxLayout, QLabel, QComboBox, QLayout
from PySide6.QtCore import Qt


class Button(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("Button")

        self.setMinimumHeight(20)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)


class ComboBox(QWidget):
    def __init__(self, label_text, options):
        super().__init__()
        self.setObjectName("ComboBox")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetFixedSize)

        self.label = QLabel(label_text)
        self.combo_box = QComboBox()
        self.combo_box.addItems(options)

        layout.addWidget(self.label)
        layout.addWidget(self.combo_box)

    def get_text(self):
        return self.combo_box.currentText()


class Headline(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("Headline")

        self.setContentsMargins(5, 0, 0, 0)
        self.setAlignment(Qt.AlignLeft)


class ProgressBar(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setObjectName("ProgressBar")

        self.setTextVisible(False)
        self.setRange(0, 0)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(4)
