from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Qt, QObject
import numpy as np
from inspect import signature

from ..shared.fit_runner import FitRunner
from ..shared.check_bounds_with_message_box import check_bounds_with_message_box
from ..shared.param_names_unicode import param_names_unicode
from ..shared.param_bounds import param_bounds

from .read_xlsx import read_xlsx
from ..calibration_window.calibration_window import CalibrationWindow


class MainWindowLogic(QObject):
    def __init__(self, main_window, engine):
        super().__init__()
        self.ui = main_window

        self.MODEL_SELECT_OPTIONS = {
            "Single Exposure": engine.models.expo,
            "Exposure-Burial":engine.models.expo_buri,
            "Exposure-Burial-Exposure": engine.models.expo_buri_expo,
            "Exposure-Burial-Exposure-Burial":
                engine.models.expo_buri_expo_buri,
            }
        self.FIT_QUALITY_OPTIONS = {
            "low": engine.fit_quality_settings.low,
            "medium": engine.fit_quality_settings.medium,
            "high": engine.fit_quality_settings.high,
            "very high": engine.fit_quality_settings.very_high
        }

        self.engine = engine
        self.fit_runner = None

        # input data
        self.x_data = None
        self.y_data = None
        self.y_err_std = None

        self.known_params = None
        self.known_params_err_std = None
        self.model_function = None

        # fit result
        self.fit_result = None

    def load_xlsx(self):
        """Opens a file dialog to open the data and plots them on the screen."""

        if self.fit_runner is not None:
            QMessageBox.warning(self.ui, "Warning",
                "Wait until the current fit has finished.")
            return

        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open .xlsx File",
            "", "Excel Files (*.xlsx);;All Files (*)")
        if filename:
            self.x_data, self.y_data, self.y_err_std \
                = read_xlsx(filename)
            self.ui.plot_widget.clear()
            self.ui.plot_widget.scatter(self.x_data, self.y_data,
                y_err_data=self.y_err_std)

    def open_calibration_window(self):
        """Opens the calibration window."""

        if self.fit_runner is not None:
            QMessageBox.warning(self.ui, "Warning",
                "Wait until the current fit has finished.")
            return

        if self.ui.calibration_window is None \
            or not self.ui.calibration_window.isVisible():
            self.ui.calibration_window = CalibrationWindow()
            self.ui.calibration_window.show()
        else:
            self.ui.calibration_window.raise_()
            self.ui.calibration_window.activateWindow()

    def run_fit(self, fit_type):
        if self.fit_runner is not None:
            QMessageBox.warning(self.ui, "Warning", "A fit is already running.")
            return
        if self.x_data is None:
            QMessageBox.warning(self.ui, "Warning", "No data loaded.")
            return

        # get parameter values with stds for all input parameters from the ui
        # input table
        input_parameter_table = self.ui.input_parameter_table
        input_parameter_names = input_parameter_table.INPUT_PARAMETER_NAMES

        self.known_params = {
            param_name: input_parameter_table.get_value(param_name) \
            for param_name in input_parameter_names}

        self.known_params_err_std = {
            param_name: input_parameter_table.get_std(param_name) \
            for param_name in input_parameter_names}

        # decrement order by 1, see models.py for documentation
        self.known_params["order"] -= 1.0

        # get the fit quality and model function from the ui combo boxes
        fit_quality_select = self.ui.quality_select.get_text()
        fit_quality = self.FIT_QUALITY_OPTIONS[fit_quality_select]
        model_function_select = self.ui.model_select.get_text()
        self.model_function = self.MODEL_SELECT_OPTIONS[model_function_select]

        # retrieve model function arguments
        model_arguments = signature(self.model_function).parameters

        # filter known_params and known_params_err_std to only hold arguments
        # of the selected model function
        # (e.g. F is not necessary for single exposure)
        self.known_params = {
            param_name: value for param_name, value \
            in self.known_params.items() if param_name in model_arguments}
        self.known_params_err_std = {
            param_name: value for param_name, value \
            in self.known_params_err_std.items() \
            if param_name in model_arguments}

        # check if the user submitted numbers that lie within the bounds for the
        # parameter values and standard deviations, if not show an alert box and
        # abort the fit
        for param_name, value in self.known_params.items():
            if not check_bounds_with_message_box(self.ui, value,
                param_bounds.val.asdict()[param_name],
                param_names_unicode.asdict()[param_name]):
                return
        # standard deviations of known parameters are only relevant for mcmc fit
        if fit_type == "mcmc":
            for param_name, value in self.known_params_err_std.items():
                if not check_bounds_with_message_box(self.ui, value,
                    param_bounds.std.asdict()[param_name],
                    param_names_unicode.asdict()[param_name], std=True):
                    return

        # get a list of all free/fit parameter names
        free_params = [param_name for param_name in model_arguments \
            if param_name not in self.known_params.keys()]

        # get bounds for the free parameters
        # (needed for the global initial guess finder)
        bounds = {param_name: value for param_name, value \
            in param_bounds.val.asdict().items() if param_name in free_params}

        # clear result table and plot
        self.ui.result_table.clear()
        self.ui.plot_widget.clear_plot()

        # run fit 
        self.fit_runner = FitRunner(self.engine, self.x_data,
            self.y_data, self.y_err_std, self.model_function, self.known_params,
            bounds, fit_type, known_params_err_std=self.known_params_err_std,
            fit_quality=fit_quality)

        self.fit_runner.status.connect(self.ui.status_label.setText)
        self.fit_runner.finished.connect(self.on_fit_finished,
            Qt.QueuedConnection)
        self.fit_runner.failed.connect(self.on_fit_failed,
            Qt.QueuedConnection)
        self.fit_runner._thread.finished.connect(self.clear_fit_runner,
            Qt.QueuedConnection)

        self.ui.progress_bar.setVisible(True)
        self.ui.status_label.setVisible(True)

        self.fit_runner.start()

    def on_fit_finished(self):
        self.ui.progress_bar.setVisible(False)
        self.ui.status_label.setVisible(False)

        self.fit_result = self.fit_runner.result

        if not self.fit_result.success:
            QMessageBox.warning(self.ui, "Warning",
                "There have been problems with the fit. The results may be "
                "faulty. Try increasing the fit quality, or improving the "
                "accuracy of the known parameters.")
        print(self.fit_result)

        for param_name, value in self.fit_result.best_fit.items():
            self.ui.result_table.set_result(param_name, value)

        if self.fit_result.confidence_interval is not None:
            for param_name, interval \
                in self.fit_result.confidence_interval.items():
                self.ui.result_table.set_confidence_interval(
                    param_name, interval)

        if self.fit_result.samples is not None:
            event_ages, event_ages_samples = self.engine.get_event_ages(
                list(self.fit_result.best_fit.keys()), self.fit_result.samples)

            for param_name, (value, interval) in event_ages.items():
                self.ui.result_table.set_result(param_name, value)
                self.ui.result_table.set_confidence_interval(param_name,
                    interval)

            all_samples = self.fit_result.samples | event_ages_samples
            for param_name, samples in all_samples.items():
                self.ui.result_table.set_posterior_samples(param_name, samples)

        # plot fitted curve
        x_data_fit = np.linspace(np.min(self.x_data), np.max(self.x_data), 200)
        y_data_fit = self.model_function(x_data_fit, **self.known_params,
            **self.fit_result.best_fit)
        self.ui.plot_widget.plot(x_data_fit, y_data_fit)

    def on_fit_failed(self, message):
        self.ui.progress_bar.setVisible(False)
        self.ui.status_label.setVisible(False)
        QMessageBox.critical(self.ui, "Error",
            "Fit crashed. This should not happen. Could be caused by bad input "
            f"data or bad input parameters. \n\nError message: \n{message}")

    def clear_fit_runner(self):
        self.fit_runner = None
