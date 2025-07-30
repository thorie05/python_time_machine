from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

class CalibrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibration")
