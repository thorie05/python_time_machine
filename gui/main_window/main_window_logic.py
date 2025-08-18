from inspect import signature

import numpy as np
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTextEdit

from ..calibration_window.calibration_window import CalibrationWindow
from ..shared.basic_widgets import MessageBoxFitCrash
from ..shared.fit_runner import FitRunner
from ..shared.read_write_xlsx import read_xlsx, write_xlsx
from ..shared.style_config import param_names_unicode, style_tokens


class MainWindowLogic(QObject):
    def __init__(self, main_window, engine):
        super().__init__()
        self.ui = main_window # store main window class to access ui elements
        self.engine = engine

        self.calibration_window = None
        self.fit_runner = None

        self.MODEL_SELECT_OPTIONS = {
            "Single Exposure": self.engine.models.expo,
            "Exposure-Burial":self.engine.models.expo_buri,
            "Exposure-Burial-Exposure": self.engine.models.expo_buri_expo,
            "Exposure-Burial-Exposure-Burial":
                self.engine.models.expo_buri_expo_buri,
        }
        self.FIT_TYPE_OPTIONS = {
            "Least-squares fit": "easy",
            "MCMC fit": "mcmc"
        }
        self.FIT_QUALITY_OPTIONS = {
            "low": self.engine.fit_quality_settings.low,
            "medium": self.engine.fit_quality_settings.medium,
            "high": self.engine.fit_quality_settings.high,
            "very high": self.engine.fit_quality_settings.very_high
        }

        # input data
        self.x_data = None
        self.y_data = None
        self.y_err_std = None
        self.known_params = None
        self.known_params_err_std = None
        self.bounds = None

        self.model_function = None
        self.fit_type = None
        self.fit_quality = None 

        # fit results
        self.initial_guess = None
        self.bootstrap_estimation = None
        self.fit_result = None

    def open_calibration_window(self):
        """Opens the calibration window."""

        # only allow opening the calibration window when no fit is running
        if self.fit_runner is not None:
            QMessageBox.warning(self.ui, "Warning",
                "Wait until the current fit has finished.")
            return

        if self.ui.calibration_window is None:
            self.ui.calibration_window = CalibrationWindow(self.engine,
                self.apply_calibration_results)
            self.ui.calibration_window.setAttribute(Qt.WA_DeleteOnClose, True)

            self.ui.calibration_window.destroyed.connect(
                lambda _=None: setattr(self.ui, "calibration_window", None))

            self.ui.calibration_window.show()
        else:
            self.ui.calibration_window.raise_()
            self.ui.calibration_window.activateWindow()

    def load_xlsx(self):
        """Opens a file dialog to open fitting data and plots it."""

        # only allow selecting new data when no fit is running
        if self.fit_runner is not None:
            QMessageBox.warning(self.ui, "Warning",
                "Wait until the current fit has finished.")
            return

        # open qt file dialog
        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open .xlsx File",
            "", "Excel Files (*.xlsx);;All Files (*)")
        if filename:
            # read xlsx data
            sheet_data = read_xlsx(filename)
            if len(sheet_data.keys()) != 1:
                QMessageBox.warning(self.ui, "Warning", ".xlsx file must "
                "consist of exactly one data sheet.")
                return

            # check if shapes match
            (self.x_data, self.y_data, self.y_err_std), = sheet_data.values()
            if not (self.x_data.shape == self.y_data.shape \
                == self.y_err_std.shape):
                QMessageBox.warning(self.ui, "Warning", ".xlsx sheet must "
                "consist of three columns of the same height (Depth, Lx/Tx "
                "and Error).")
                return

            # clear result table and plot
            self.ui.result_table.clear()
            self.ui.plot_widget.clear()

            # scatter the new datapoints
            self.ui.plot_widget.scatter(self.x_data, self.y_data,
                y_err_data=self.y_err_std,
                color=style_tokens.plot.single_scatter_color)

    def run_fit(self):
        """Run fit function that is connected to the run fit buttons."""

        if self.fit_runner is not None:
            QMessageBox.warning(self.ui, "Warning", "A fit is already running.")
            return
        if self.x_data is None:
            QMessageBox.warning(self.ui, "Warning", "No data loaded.")
            return
        if self.ui.calibration_window is not None:
            QMessageBox.warning(self.ui, "Warning", "The calibration window "
                "needs to be closed.")
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

        # decrement order by 1, see fitting engine models
        self.known_params["order"] -= 1.0

        # get the fit type, quality and model function from the ui combo boxes
        fit_type_select = self.ui.fit_type_select.get_text()
        self.fit_type = self.FIT_TYPE_OPTIONS[fit_type_select]
        fit_quality_select = self.ui.fit_quality_select.get_text()
        self.fit_quality = self.FIT_QUALITY_OPTIONS[fit_quality_select]
        model_select = self.ui.model_select.get_text()
        self.model_function = self.MODEL_SELECT_OPTIONS[model_select]

        # retrieve model function arguments
        model_arguments = signature(self.model_function).parameters

        # filter known_params and known_params_err_std to only hold arguments
        # of the selected model function
        # (F is not necessary for single exposure, for example)
        self.known_params = {
            param_name: value for param_name, value \
            in self.known_params.items() if param_name in model_arguments}
        self.known_params_err_std = {
            param_name: value for param_name, value \
            in self.known_params_err_std.items() \
            if param_name in model_arguments}

        # check that all input parameters lie within the specified bounds
        # if not show alert box and abort the fit
        for param_name in self.known_params:
            value_val = self.known_params[param_name]
            value_std = self.known_params_err_std[param_name]
            lower_val, upper_val \
                = self.engine.param_bounds.val.asdict()[param_name]
            lower_std, upper_std \
                = self.engine.param_bounds.std.asdict()[param_name]
            param_name_unicode = param_names_unicode.asdict()[param_name]

            # always check known values
            if not (lower_val <= value_val <= upper_val):
                # increment order bounds by 1 for ui, see models for details
                if param_name == "order":
                    lower_val += 1
                    upper_val += 1
                QMessageBox.warning(self.ui, "Warning", 
                    f"{param_name_unicode} must lie between {lower_val} and "
                    f"{upper_val}")
                return

            # standard deviations are only relevant for the mcmc fit
            if self.fit_type == "mcmc":
                if not (lower_std <= value_std <= upper_std):
                    QMessageBox.warning(self.ui, "Warning",
                        f"Standard deviation of {param_name_unicode} must lie "
                        f"between {lower_std} and {upper_std}")
                    return

        # hide export fit button
        self.ui.export_button.setVisible(False)

        # clear result table and previous fitted function
        self.ui.result_table.clear()
        self.ui.plot_widget.clear_only_plot()

        self.ui.progress_bar.setVisible(True)
        self.ui.status_label.setVisible(True)

        # get a list of all free/fit parameter names
        free_params = [param_name for param_name in model_arguments \
            if param_name not in self.known_params.keys()]

        # get bounds for the free parameters (needed initial guess finder)
        self.bounds = {param_name: value for param_name, value \
            in self.engine.param_bounds.val.asdict().items() \
            if param_name in free_params}

        # run fit 
        self.fit_runner = FitRunner(self.engine, self.x_data,
            self.y_data, self.y_err_std, self.model_function, self.known_params,
            self.bounds, self.fit_type,
            known_params_err_std=self.known_params_err_std,
            fit_quality=self.fit_quality)

        self.fit_runner.status.connect(self.ui.status_label.setText)
        self.fit_runner.finished.connect(self.on_fit_finished,
            Qt.QueuedConnection)
        self.fit_runner.failed.connect(self.on_fit_failed,
            Qt.QueuedConnection)
        self.fit_runner._thread.finished.connect(self.clear_fit_runner,
            Qt.QueuedConnection)

        self.fit_runner.start()

    def on_fit_finished(self):
        """Function that is called when a fit finishes."""

        # save fit result
        self.fit_result = self.fit_runner.fit_result

        # check that the fit results are reliable
        if not self.fit_result.success:
            QMessageBox.warning(self.ui, "Warning",
                "There have been problems with the fit. The results may be "
                "faulty. Try increasing the fit quality, or improving the "
                "accuracy of the known parameters.")

        # hide progres bar and status label
        self.ui.progress_bar.setVisible(False)
        self.ui.status_label.setVisible(False)

        # show export fit button only on for mcmc fit
        if self.fit_result.samples:
            self.ui.export_button.setVisible(True)

        print(self.fit_result) # debug

        # set fit parameter results in the result table
        for param_name, value in self.fit_result.best_fit.items():
            self.ui.result_table.set_result(param_name, value)

        # set confidedence intervals in the result table (only after mcmc fit)
        if self.fit_result.confidence_interval is not None:
            for param_name, interval \
                in self.fit_result.confidence_interval.items():
                self.ui.result_table.set_confidence_interval(
                    param_name, interval)

        # set event ages and posterior samples (only after mcmc fit)
        if self.fit_type == "mcmc":
            # calculate event ages from posterior samples
            event_ages, event_ages_samples = self.engine.get_event_ages(
                list(self.fit_result.best_fit.keys()), self.fit_result.samples)

            # set event ages with confidence intervals
            for param_name, (value, interval) in event_ages.items():
                self.ui.result_table.set_result(param_name, value)
                self.ui.result_table.set_confidence_interval(param_name,
                    interval)

            # connect posterior samples to be displayed in a historgam
            all_samples = self.fit_result.samples | event_ages_samples
            for param_name, samples in all_samples.items():
                self.ui.result_table.set_posterior_samples(param_name, samples)

        # plot fit curve
        x_data_fit = np.linspace(np.min(self.x_data), np.max(self.x_data), 200)
        y_data_fit = self.model_function(x_data_fit, **self.known_params,
            **self.fit_result.best_fit)
        self.ui.plot_widget.plot(x_data_fit, y_data_fit,
            color=style_tokens.plot.single_plot_color)

    def on_fit_failed(self, message):
        """Function that is called when a fit raises an error."""

        # hide progress bar
        self.ui.progress_bar.setVisible(False)
        self.ui.status_label.setVisible(False)

        # create message box
        msg_box = MessageBoxFitCrash(message, parent=self.ui)
        msg_box.exec()

    def clear_fit_runner(self):
        """Destroys the current fit runner."""

        self.fit_runner = None

    def export_mcmc_fit(self):
        if self.fit_type != "mcmc":
            QMessageBox.warning(self.ui, "Warning", "No MCMC fit completed.")
            return

        path, _ = QFileDialog.getSaveFileName(self.ui,
            caption="Save fit result as Excel file", dir="",
            filter="Excel Workbook (*.xlsx)")
        if not path:
            return None
        if not path.endswith(".xlsx"):
            path += ".xlsx"

        write_xlsx(path)

    def apply_calibration_results(self, sigma_phi, sigma_phi_std, mu, mu_std):
        self.ui.input_parameter_table.set_value("sigma_phi", sigma_phi)
        self.ui.input_parameter_table.set_std("sigma_phi", sigma_phi_std)
        self.ui.input_parameter_table.set_value("mu", mu)
        self.ui.input_parameter_table.set_std("mu", mu_std)
