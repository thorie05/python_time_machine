from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QMessageBox,
    QVBoxLayout,
    QWidget
)

from .calibration_parameter_table import CalibrationParameterTable
from .calibration_samples_table import CalibrationSamplesTable
from .calibration_window_logic import CalibrationWindowLogic
from ..shared.basic_widgets import Button, ComboBox, Headline, ProgressBar
from ..shared.plots import Plot
from ..shared.style_config import style_tokens


class CalibrationWindow(QWidget):
    """
    The calibration window widget.

    Hosts the widgets and connects them to logic from calibration_window_logic.
    """

    def __init__(self, engine, apply_calibration_results_main_window_func):
        super().__init__()
        self.setObjectName("CalibrationWindow")

        # store logic methods to connect them with widgets
        self.logic = CalibrationWindowLogic(self, engine,
            apply_calibration_results_main_window_func)

        # flag for forcing the close of the window even when a fit is running
        self._force_close = False

        # functional widgets are stored as attributes for later access
        self.calibration_parameter_table = CalibrationParameterTable(engine)
        self.calibration_samples_table = CalibrationSamplesTable()
        self.plot_widget = Plot()
        self.fit_quality_select = ComboBox("Select fit quality:",
            list(self.logic.FIT_QUALITY_OPTIONS.keys()))
        self.fit_type_select = ComboBox("Select fit type:",
            self.logic.FIT_TYPE_OPTIONS)
        self.load_button = Button("Choose .xlsx data")
        self.filename_label = QLabel("")
        self.run_fit_button = Button("Run calibration")
        self.export_button = Button("Export MCMC results")
        self.apply_button = Button("Apply calibration results")
        self.progress_bar = ProgressBar()
        self.status_label = QLabel()

        # create calibration window
        self.setWindowTitle(style_tokens.calibration_window.window_title)
        self.resize(style_tokens.calibration_window.default_width,
            style_tokens.calibration_window.default_height)

        # outer layout
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(
            style_tokens.calibration_window.outer_margin,
            style_tokens.calibration_window.outer_margin,
            style_tokens.calibration_window.outer_margin,
            style_tokens.calibration_window.outer_margin_lower)

        # content area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # add top row (tables with headlines)
        top_row = self.create_top_row()
        content_layout.addLayout(top_row, stretch=1)

        # add bottom row (plot widget and button column)
        bottom_row = self.create_bottom_row()
        content_layout.addLayout(bottom_row, stretch=3)

        outer_layout.addLayout(content_layout, 1)
        self.setLayout(outer_layout)

    def create_top_row(self):
        """Creates the top row with the samples and results tables."""

        top_row = QHBoxLayout()
        top_row.setSpacing(style_tokens.calibration_window.top_row_spacing)

        # fitting result table with headline
        result_column = QVBoxLayout()
        result_column.addWidget(Headline("Calibration Parameters"))
        result_column.addWidget(self.calibration_parameter_table)
        top_row.addLayout(result_column, stretch=5)

        # samples table with headline
        samples_column = QVBoxLayout()
        samples_column.addWidget(Headline("Calibration Samples"))
        samples_column.addWidget(self.calibration_samples_table)
        top_row.addLayout(samples_column, stretch=4)

        return top_row

    def create_bottom_row(self):
        """Creates the bottom row with the plot and the button column."""

        bottom_row = QHBoxLayout()

        # plot_widget
        bottom_row.addWidget(self.plot_widget, stretch=4)

        # create button column containing all buttons and combo boxes
        button_column = QVBoxLayout()
        button_column.setSpacing(
            style_tokens.calibration_window.button_column_spacing)
        button_column.setContentsMargins(
            0, style_tokens.calibration_window.button_column_top_margin, 0, 0)

        # load .xslx button and filename in a row
        load_button_row = QHBoxLayout()
        load_button_row.setAlignment(Qt.AlignLeft)
        load_button_row.addWidget(self.load_button)
        self.load_button.clicked.connect(self.logic.load_xlsx)
        load_button_row.addWidget(self.filename_label)
        button_column.addLayout(load_button_row)

        # combo boxes for fit type and quality selection
        button_column.addWidget(self.fit_type_select)
        # set mcmc as default fit type
        self.fit_type_select.combo_box.setCurrentIndex(1)
        button_column.addWidget(self.fit_quality_select)
        # set medium as default value for fit quality
        self.fit_quality_select.combo_box.setCurrentIndex(1)

        # run fit and export buttons in a row
        run_button_row = QHBoxLayout()
        run_button_row.setAlignment(Qt.AlignLeft)
        run_button_row.addWidget(self.run_fit_button)
        self.run_fit_button.clicked.connect(self.logic.run_fit)
        run_button_row.addWidget(self.export_button)
        self.export_button.clicked.connect(self.logic.export_mcmc_fit)
        button_column.addLayout(run_button_row)

        # apply calibration results button
        button_column.addWidget(self.apply_button)
        self.apply_button.clicked.connect(self.logic.apply_calibration_results)

        # loading bar and label
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(2) # smaller spacing between bar and label
        progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        self.status_label.setVisible(False)
        progress_layout.addWidget(self.status_label)
        button_column.addLayout(progress_layout)

        # add stretch so that the buttons stack from top instead of spacing
        # evenly
        button_column.addStretch(1)

        bottom_row.addLayout(button_column, stretch=1)

        return bottom_row

    def closeEvent(self, event):
        """Prevents the close of the calibration window if a fit is running."""

        # skip the check if the force close flag is active
        if not self._force_close:
            if self.logic.fit_runner:
                QMessageBox.warning(self, "Warning",
                    "The calibration window can't be closed while a fit is "
                    " running. Close the main window to exit the app.")
                event.ignore()
                return

        super().closeEvent(event)

    def force_close(self):
        """Forces the close of the calibration even if a fit is running."""

        self._force_close = True
        self.close()
