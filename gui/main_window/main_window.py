from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from functools import partial

from .main_window_logic import MainWindowLogic

from ..shared.plot import Plot
from .. shared.standard_widgets import StandardButton, StandardComboBox, \
    StandardHeadline, StandardProgressBar, ui_style

from .input_parameter_table import InputParameterTable
from .result_table import ResultTable


class MainWindow(QWidget):
    def __init__(self, engine):
        super().__init__()

        self.logic = MainWindowLogic(self, engine)

        # these widgets need to be stored as arguments because they encompass
        # functionality and aren't purely visual -> later access is necessary
        self.calibration_window = None
        self.input_parameter_table = InputParameterTable(self.logic.engine)
        self.result_table = ResultTable()
        self.plot_widget = Plot()
        self.calibration_button = StandardButton("Calibrate")
        self.quality_select = StandardComboBox("Select fit quality:",
            list(self.logic.fit_quality_options.keys()))
        self.model_select = StandardComboBox("Select model:",
            list(self.logic.model_select_options.keys()))
        self.load_button = StandardButton("Choose .xlsx data")
        self.run_mcmc_button = StandardButton("Run MCMC fit")
        self.run_easy_button = StandardButton("Run least-squares fit")
        # progress bar and label
        self.progress_bar = StandardProgressBar()
        self.status_label = QLabel()

        # create main window
        self.setWindowTitle("Python Time Machine")
        self.resize(ui_style.main_window.default_width,
            ui_style.main_window.default_height)
        self.setStyleSheet(
            f"background-color: {ui_style.main_window.background_color};")

        # outer layout
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(ui_style.main_window.outer_margin,
            ui_style.main_window.outer_margin,
            ui_style.main_window.outer_margin, 0)
        outer_layout.setSpacing(ui_style.main_window.inner_window_spacing)

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
        """Creates the top row.
        
        Creates the top row with the input parameter table with its headline as
        well as the results table with its headline.
        """

        top_row = QHBoxLayout()

        # input parameter table with headline
        input_column = QVBoxLayout()
        input_column.addWidget(StandardHeadline("Parameter Inputs"))
        input_column.addWidget(self.input_parameter_table)
        top_row.addLayout(input_column, stretch=1)

        # result table with headline
        result_column = QVBoxLayout()
        result_column.addWidget(StandardHeadline("Fitting Results"))
        result_column.addWidget(self.result_table)
        # gets more stretch because it hase more columns
        top_row.addLayout(result_column, stretch=2)

        return top_row

    def create_bottom_row(self):
        """Creates the bottom row.

        Creates the bottom row with the main plot on the left side and a column
        containing the relevant buttons on the right side.
        """

        bottom_row = QHBoxLayout()

        # plot_widget
        self.plot_widget.setMinimumHeight(400)
        bottom_row.addWidget(self.plot_widget, stretch=4)

        # create button column containing all buttons and combo boxes
        button_column = QVBoxLayout()
        button_column.setSpacing(20) 
        button_column.setContentsMargins(0, 50, 0, 0)

        # calibration button
        self.calibration_button.clicked.connect(
            self.logic.open_calibration_window)
        self.calibration_button.setFocusPolicy(Qt.NoFocus)
        button_column.addWidget(self.calibration_button)

        # load .xslx button
        self.load_button.clicked.connect(self.logic.load_xlsx)
        self.load_button.setFocusPolicy(Qt.NoFocus)
        button_column.addWidget(self.load_button)

        # combo box for model selection
        button_column.addWidget(self.model_select)

        # combo box for fit quality selection
        button_column.addWidget(self.quality_select)
        # set default value to medium
        self.quality_select.combo_box.setCurrentIndex(1)

        # run mcmc fit button
        self.run_mcmc_button.clicked.connect(partial(self.logic.run_fit,
            "mcmc"))
        self.run_mcmc_button.setFocusPolicy(Qt.NoFocus)

        # run least squares fit button
        self.run_easy_button.clicked.connect(partial(self.logic.run_fit,
            "easy"))
        self.run_easy_button.setFocusPolicy(Qt.NoFocus)

        # layout to place both buttons side-by-side, left-aligned
        fit_button_row = QHBoxLayout()
        fit_button_row.setAlignment(Qt.AlignLeft)
        fit_button_row.addWidget(self.run_mcmc_button)
        fit_button_row.addWidget(self.run_easy_button)

        # Add the row to the button_column layout
        button_column.addLayout(fit_button_row)

        # loading bar and label in a tight sub-layout
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(2)  # smaller spacing between bar and label
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
