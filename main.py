from PySide6.QtWidgets import QApplication
import sys

from gui.main_window import MainWindow
from fitting_engine import FittingEngine


def main():
    """Main function."""

    app = QApplication()

    engine = FittingEngine()

    window = MainWindow(engine)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
