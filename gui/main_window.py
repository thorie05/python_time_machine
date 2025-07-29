from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, \
    QLabel


class MainWindow(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.setWindowTitle("Python Time Machine")
        self.resize(1200, 800)
        self.engine = engine

        # UI Setup
        layout = QVBoxLayout()

        self.result_label = QLabel("Result:")
        layout.addWidget(self.result_label)

        fit_button = QPushButton("Run Fit")
        layout.addWidget(fit_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
