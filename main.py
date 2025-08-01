from PySide6.QtWidgets import QApplication
import sys
import os

from gui.main_window.main_window import MainWindow
from fitting_engine import FittingEngine


def main():
    """Main function."""

    verbose = "--verbose" in sys.argv

    app = QApplication()
    engine = FittingEngine(verbose=True) # only true for debugging
    window = MainWindow(engine)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
