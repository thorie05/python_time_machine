from PySide6.QtWidgets import QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QMessageBox
from PySide6.QtCore import Qt
import numpy as np

from ..shared.fit_runner import FitRunner
from ..shared.plot import Plot
from .. shared.standard_widgets import StandardButton, StandardComboBox, \
    StandardHeadline, StandardProgressBar, ui_style

from .input_parameter_table import InputParameterTable
from .result_table import ResultTable
from .read_xlsx import read_xlsx
from ..calibration_window.calibration_window import CalibrationWindow

MODEL_SELECT_OPTIONS = ["Single Exposure", "Exposure-Burial",
    "Exposure-Burial-Exposure", "Exposure-Burial-Exposure-Burial"]
FIT_QUALITY_OPTIONS = ["low", "medium", "high", "very high"]


class MainWindow(QWidget):
    def __init__(self, engine):
        super().__init__()

        self.engine = engine
        self.fit_runner = None

        # input data
        self.x_data = None
        self.y_data = None
        self.y_err_std = None

        # input parameters
        self.order = None
        self.order_std = None
        self.sigma_phi = None
        self.sigma_phi_std = None
        self.mu = None
        self.mu_std = None
        self.f = None
        self.f_std = None

        # fit results
        self.model_function = None
        self.t_exposure_1 = None
        self.t_exposure_1_confidence_interval = None
        self.t_burial_1 = None
        self.t_burial_1_confidence_interval = None
        self.t_exposure_2 = None
        self.t_exposure_2_confidence_interval = None
        self.t_burial_2 = None
        self.t_since_burial_2_confidence_interval = None
        self.t_since_exposure_1 = None
        self.t_since_exposure_1_confidence_interval = None
        self.t_since_burial_1 = None
        self.t_since_burial_1_confidence_interval = None
        self.t_since_exposure_2 = None
        self.t_since_exposure_2_confidence_interval = None
        self.t_since_burial_2 = None
        self.t_since_burial_2_confidence_interval = None

        # these widgets need to be stored as arguments because they encompass
        # functionality and aren't purely visual -> later access is necessary
        self.calibration_window = None
        self.input_parameter_table = InputParameterTable(self.engine)
        self.result_table = ResultTable()
        self.plot_widget = Plot()
        self.calibration_button = StandardButton("Calibrate")
        self.quality_select = StandardComboBox("Select fit quality:",
            FIT_QUALITY_OPTIONS)
        self.model_select = StandardComboBox("Select model:",
            MODEL_SELECT_OPTIONS)
        self.load_button = StandardButton("Choose .xlsx data")
        self.run_button = StandardButton("Run fit")
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
        self.calibration_button.clicked.connect(self.open_calibration_window)
        self.calibration_button.setFocusPolicy(Qt.NoFocus)
        button_column.addWidget(self.calibration_button)

        # load .xslx button
        self.load_button.clicked.connect(self.load_xlsx)
        self.load_button.setFocusPolicy(Qt.NoFocus)
        button_column.addWidget(self.load_button)

        # combo box for model selection
        button_column.addWidget(self.model_select)

        # combo box for fit quality selection
        button_column.addWidget(self.quality_select)
        # set default value to medium
        self.quality_select.combo_box.setCurrentIndex(1)

        # run fit button
        self.run_button.clicked.connect(self.run_fit)
        self.run_button.setFocusPolicy(Qt.NoFocus)
        button_column.addWidget(self.run_button)

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

    def load_xlsx(self):
        """Opens a file dialog to open the data and plots them on the screen."""

        if self.fit_runner is not None:
            QMessageBox.warning(self, "Warning",
                "Wait until the current fit has finished.")
            return

        filename, _ = QFileDialog.getOpenFileName(self, "Open .xlsx File",
            "", "Excel Files (*.xlsx);;All Files (*)")
        if filename:
            self.x_data, self.y_data, self.y_err_std = read_xlsx(filename)
            self.plot_widget.clear()
            self.plot_widget.scatter(self.x_data, self.y_data,
                y_err_data=self.y_err_std)

    def open_calibration_window(self):
        """Opens the calibration window."""

        if self.fit_runner is not None:
            QMessageBox.warning(self, "Warning",
                "Wait until the current fit has finished.")
            return

        if self.calibration_window is None \
            or not self.calibration_window.isVisible():
            self.calibration_window = CalibrationWindow()
            self.calibration_window.show()
        else:
            self.calibration_window.raise_()
            self.calibration_window.activateWindow()

    def run_fit(self):
        if self.fit_runner is not None:
            QMessageBox.warning(self, "Warning", "A fit is already running.")
            return
        if self.x_data is None:
            QMessageBox.warning(self, "Warning", "No data loaded.")
            return

        self.result_table.clear_table()

        model_function_select = self.model_select.get_text()
        fit_quality = self.quality_select.get_text()

        self.order = self.input_parameter_table.get_order()
        self.order_std = self.input_parameter_table.get_order_std()
        self.sigma_phi = self.input_parameter_table.get_sigma_phi()
        self.sigma_phi_std = self.input_parameter_table.get_sigma_phi_std()
        self.mu = self.input_parameter_table.get_mu()
        self.mu_std = self.input_parameter_table.get_mu_std()
        self.f = self.input_parameter_table.get_f()
        self.f_std = self.input_parameter_table.get_f_std()

        known_params = {"order": self.order, "sigma_phi": self.sigma_phi,
            "mu": self.mu}
        known_params_err_std = {"order": self.order_std,
            "sigma_phi": self.sigma_phi_std, "mu": self.mu_std}

        if not (self.engine.bounds.order[0] <= self.order \
            <= self.engine.bounds.order[1]):
            QMessageBox.warning(self, "Warning",
                f"order must lie between {self.engine.bounds.order[0] + 1} and "
                f"{self.engine.bounds.order[1] + 1}.")
            return
        if not (self.engine.bounds.order_std[0] <= self.order_std \
            <= self.engine.bounds.order_std[1]):
            QMessageBox.warning(self, "Warning",
                f"Standard deviation of order must lie between "
                f"{self.engine.bounds.order_std[0]} and "
                f"{self.engine.bounds.order_std[1]}.")
            return
        if not (self.engine.bounds.sigma_phi[0] <= self.sigma_phi \
            <= self.engine.bounds.sigma_phi[1]):
            QMessageBox.warning(self, "Warning",
                f"<span style='text-decoration: overline;'>σφ</span>"
                f"<sub>0</sub> must lie between "
                f"{self.engine.bounds.sigma_phi[0]} and "
                f"{self.engine.bounds.sigma_phi[1]}.")
            return
        if not (self.engine.bounds.sigma_phi_std[0] <= self.sigma_phi_std \
            <= self.engine.bounds.sigma_phi_std[1]):
            QMessageBox.warning(self, "Warning",
                f"Standard deviation of <span style='text-decoration: "
                f"overline;'>σφ</span><sub>0</sub> must lie between "
                f"{self.engine.bounds.sigma_phi_std[0]} and "
                f"{self.engine.bounds.sigma_phi_std[1]}.")
            return
        if not (self.engine.bounds.mu[0] <= self.mu \
            <= self.engine.bounds.mu[1]):
            QMessageBox.warning(self, "Warning",
                f"µ must lie between {self.engine.bounds.mu[0]} and "
                f"{self.engine.bounds.mu[1]}.")
            return
        if not (self.engine.bounds.mu_std[0] <= self.mu_std \
            <= self.engine.bounds.mu_std[1]):
            QMessageBox.warning(self, "Warning",
                f"Standard deviation of µ must lie between "
                f"{self.engine.bounds.mu_std[0]} and "
                f"{self.engine.bounds.mu_std[1]}.")
            return

        bounds = {"order": self.engine.bounds.order,
            "sigma_phi": self.engine.bounds.sigma_phi,
            "mu": self.engine.bounds.mu,
            "t_exposure_1": self.engine.bounds.t_exposure_1}

        # select model function
        if model_function_select == MODEL_SELECT_OPTIONS[0]:
            self.model_function = self.engine.models.expo

        else:
            if not (self.engine.bounds.f[0] <= self.f \
                <= self.engine.bounds.f[1]):
                QMessageBox.warning(self, "Warning",
                    f"f must lie between {self.engine.bounds.f[0]} and "
                    f"{self.engine.bounds.f[1]}.")
                return
            if not (self.engine.bounds.f_std[0] <= self.f_std \
                <= self.engine.bounds.f_std[1]):
                QMessageBox.warning(self, "Warning",
                    f"Standard deviation of f must lie between "
                    f"{self.engine.bounds.f_std[0]} and "
                    f"{self.engine.bounds.f_std[1]}.")
                return

            known_params["f"] = self.f
            known_params_err_std["f"] = self.f_std
            bounds["t_burial_1"] = self.engine.bounds.t_burial_1

            if model_function_select == MODEL_SELECT_OPTIONS[1]:
                self.model_function = self.engine.models.expo_buri
            else:
                bounds["t_exposure_2"] = self.engine.bounds.t_exposure_2

                if model_function_select == MODEL_SELECT_OPTIONS[2]:
                    self.model_function = self.engine.models.expo_buri_expo
                else:
                    bounds["t_burial_2"] = self.engine.bounds.t_burial_2

                    self.model_function = self.engine.models.expo_buri_expo_buri

        self.fit_runner = FitRunner(self.engine, self.x_data, self.y_data,
            self.y_err_std, self.model_function, known_params,
            known_params_err_std, bounds, fit_quality)

        self.fit_runner.status.connect(self.status_label.setText)
        self.fit_runner.finished.connect(self.on_fit_finished,
            Qt.QueuedConnection)
        self.fit_runner.failed.connect(self.on_fit_failed,
            Qt.QueuedConnection)
        self.fit_runner._thread.finished.connect(self.clear_fit_runner,
            Qt.QueuedConnection)

        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)

        self.fit_runner.start()

    def on_fit_finished(self):
        print("a")

        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)

        print("b")

        result = self.fit_runner.result

        print("c")

        if not result.success:
            QMessageBox.warning(self, "Warning",
                "There have been problems with the fit. The results may be "
                "faulty. Try increasing the fit quality, or improving the "
                "accuracy of the known parameters.")

        bf = result.best_fit
        ci = result.confidence_interval
        ts = result.time_since_events
        ts += [(None, None) for _ in range(4 - len(ts))]

        print("d")

        # extratct results
        self.t_exposure_1 = bf.get("t_exposure_1")
        self.t_exposure_1_confidence_interval = ci.get("t_exposure_1")
        self.t_burial_1 = bf.get("t_burial_1")
        self.t_burial_1_confidence_interval = ci.get("t_burial_1")
        self.t_exposure_2 = bf.get("t_exposure_2")
        self.t_exposure_2_confidence_interval = ci.get("t_exposure_2")
        self.t_burial_2 = bf.get("t_burial_2")
        self.t_burial_2_confidence_interval = ci.get("t_burial_2")

        # extract time since results
        self.t_since_exposure_1, \
            self.t_since_exposure_1_confidence_intervals = ts[0]
        self.t_since_burial_1, \
            self.t_since_burial_1_confidence_intervals = ts[1]
        self.t_since_exposure_2, \
            self.t_since_exposure_2_confidence_intervals = ts[2]
        self.t_since_burial_2, \
            self.t_since_burial_2_confidence_intervals = ts[3]

        print("e")

        # set results with confidence intervals
        self.result_table.set_t_exposure_1(self.t_exposure_1)
        self.result_table.set_t_exposure_1_confidence_interval(
            self.t_exposure_1_confidence_interval)

        self.result_table.set_t_burial_1(self.t_burial_1)
        self.result_table.set_t_burial_1_confidence_interval(
            self.t_burial_1_confidence_interval)

        self.result_table.set_t_exposure_2(self.t_exposure_2)
        self.result_table.set_t_exposure_2_confidence_interval(
            self.t_exposure_2_confidence_interval)

        self.result_table.set_t_burial_2(self.t_burial_2)
        self.result_table.set_t_burial_2_confidence_interval(
            self.t_burial_2_confidence_interval)

        # set time since results with confidence intervals
        self.result_table.set_t_since_exposure_1(self.t_since_exposure_1)
        self.result_table.set_t_since_exposure_1_confidence_interval(
            self.t_since_exposure_1_confidence_intervals)

        self.result_table.set_t_since_burial_1(self.t_since_burial_1)
        self.result_table.set_t_since_burial_1_confidence_interval(
            self.t_since_burial_1_confidence_intervals)

        self.result_table.set_t_since_exposure_2(self.t_since_exposure_2)
        self.result_table.set_t_since_exposure_2_confidence_interval(
            self.t_since_exposure_2_confidence_intervals)

        self.result_table.set_t_since_burial_2(self.t_since_burial_2)
        self.result_table.set_t_since_burial_2_confidence_interval(
            self.t_since_burial_2_confidence_intervals)

        print("f")

        # plot fit line
        x_data_fit = np.linspace(np.min(self.x_data),
            np.max(self.x_data), 200)

        print("g")

        if self.model_function == self.engine.models.expo:
            y_data_fit = self.model_function(x_data_fit, self.order,
                self.sigma_phi, self.mu, self.t_exposure_1)
        elif self.model_function == self.engine.models.expo_buri:
            y_data_fit = self.model_function(x_data_fit, self.order,
                self.sigma_phi, self.mu, self.f, self.t_exposure_1,
                self.t_burial_1)
        elif self.model_function == self.engine.models.expo_buri_expo:
            y_data_fit = self.model_function(x_data_fit, self.order,
                self.sigma_phi, self.mu, self.f, self.t_exposure_1,
                self.t_burial_1, self.t_exposure_2)
        else:
            y_data_fit = self.engine.models.expo_buri_expo_buri(x_data_fit,
                self.order, self.sigma_phi, self.mu, self.f, self.t_exposure_1,
                self.t_burial_1, self.t_exposure_2, self.t_burial_2)

        print("h")

        self.plot_widget.plot(x_data_fit, y_data_fit)

        print("i")

        self.fit_runner = None

        print("j")

    def on_fit_failed(self, message):
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        QMessageBox.critical(self, "Error",
            "Fit crashed. This should not happen. Could be caused by bad input "
            f"data or bad input parameters. \n\nError message: \n{message}")

    def clear_fit_runner(self):
        self.fit_runner = None
