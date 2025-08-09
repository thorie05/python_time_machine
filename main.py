from PySide6.QtWidgets import QApplication
import sys
import traceback # debug: for printing tracebacks
import faulthandler # debug: for catching segfaults etc

from gui.main_window.main_window import MainWindow
from fitting_engine import FittingEngine


# debug: ensure uncaught exceptions crash the app and are printed
def exception_hook(exctype, value, tb):
    traceback.print_exception(exctype, value, tb)
    sys.exit(1)  # debug: crash app on exception


def main():
    """Main function."""

    # debug: enable crash diagnostics
    sys.excepthook = exception_hook
    faulthandler.enable()

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