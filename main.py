from PySide6.QtWidgets import QApplication
import sys

from gui.main_window.main_window import MainWindow
from fitting_engine import FittingEngine


def main():
    """Main function."""

    verbose = "--verbose" in sys.argv

    app = QApplication()
    with open("gui/shared/style.qss") as file:
        style = file.read()
    app.setStyleSheet(style)
    engine = FittingEngine(verbose=True)  # debug: verbose always True
    window = MainWindow(engine)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()