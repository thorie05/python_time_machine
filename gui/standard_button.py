from PySide6.QtWidgets import QPushButton, QSizePolicy

class StandardButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setMinimumHeight(20)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #aaa;
                padding: 3px 2px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
