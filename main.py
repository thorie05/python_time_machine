from string import Template
import sys

from PySide6.QtWidgets import QApplication

from fitting_engine import FittingEngine
from gui.main_window.main_window import MainWindow
from gui.shared.style_config import flat_style_tokens_dict


def main():
    """Main function."""

    verbose = "--verbose" in sys.argv

    app = QApplication()

    # load qss stylesheet
    with open("gui/shared/style.qss") as file:
        qss_text = file.read()

    # fill out style sheet placeholders with config values
    class DotTemplate(Template):
        idpattern = r'[a-zA-Z_][\w\.]*' # allow dots
    qss_filled = DotTemplate(qss_text).substitute(flat_style_tokens_dict)
    
    app.setStyleSheet(qss_filled)

    engine = FittingEngine(verbose=True) # debug: verbose always True
    window = MainWindow(engine)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
