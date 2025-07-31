from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLayout


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
