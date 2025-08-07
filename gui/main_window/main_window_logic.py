from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Qt, QObject
import numpy as np

from ..shared.fit_runner import FitRunner
from ..shared.bound_checker_with_message_box import BoundCheckerWithMessageBox

from .read_xlsx import read_xlsx
from ..calibration_window.calibration_window import CalibrationWindow


class MainWindowLogic(QObject):
    def __init__(self, main_window, engine):
        super().__init__()
        self.ui = main_window

        self.model_select_options = {
            "Single Exposure": engine.models.expo,
            "Exposure-Burial":engine.models.expo_buri,
            "Exposure-Burial-Exposure": engine.models.expo_buri_expo,
            "Exposure-Burial-Exposure-Burial":
                engine.models.expo_buri_expo_buri,
            }
        self.fit_quality_options = {
            "low": engine.fit_quality_settings.low,
            "medium": engine.fit_quality_settings.medium,
            "high": engine.fit_quality_settings.high,
            "very high": engine.fit_quality_settings.very_high
        }

        self.engine = engine
        self.fit_runner = None

        self.bounds_checker = BoundCheckerWithMessageBox(engine, main_window)

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

        self.model_function = None

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

        self.ui.result_table.clear_table()
        self.ui.plot_widget.clear_plot()

        fit_quality_select = self.ui.quality_select.get_text()
        fit_quality = self.fit_quality_options[fit_quality_select]
        model_function_select = self.ui.model_select.get_text()
        self.model_function = self.model_select_options[model_function_select]

        self.order = self.ui.input_parameter_table.get_order()
        self.order_std = self.ui.input_parameter_table.get_order_std()
        self.sigma_phi = self.ui.input_parameter_table.get_sigma_phi()
        self.sigma_phi_std \
            = self.ui.input_parameter_table.get_sigma_phi_std()
        self.mu = self.ui.input_parameter_table.get_mu()
        self.mu_std = self.ui.input_parameter_table.get_mu_std()
        self.f = self.ui.input_parameter_table.get_f()
        self.f_std = self.ui.input_parameter_table.get_f_std()

        known_params = {"order": self.order, "sigma_phi": self.sigma_phi,
            "mu": self.mu}
        known_params_err_std = {"order": self.order_std,
            "sigma_phi": self.sigma_phi_std, "mu": self.mu_std}
        bounds = {"order": self.engine.bounds.order,
            "sigma_phi": self.engine.bounds.sigma_phi,
            "mu": self.engine.bounds.mu,
            "t_exposure_1": self.engine.bounds.t_exposure_1}

        if not self.bounds_checker.check_order(self.order):
            return
        if not self.bounds_checker.check_sigma_phi(self.sigma_phi):
            return
        if not self.bounds_checker.check_mu(self.mu):
            return

        if fit_type == "mcmc":
            if not self.bounds_checker.check_order_std(self.order_std):
                return
            if not self.bounds_checker.check_sigma_phi_std(self.sigma_phi_std):
                return
            if not self.bounds_checker.check_mu_std(self.mu_std):
                return

        if self.model_function != self.engine.models.expo:
            if not self.bounds_checker.check_f(self.f):
                return
            if fit_type == "mcmc":
                if not self.bounds_checker.check_f_std(self.f_std):
                    return

            known_params["f"] = self.f
            known_params_err_std["f"] = self.f_std
            bounds["t_burial_1"] = self.engine.bounds.t_burial_1

            if self.model_function != self.engine.models.expo_buri:
                bounds["t_exposure_2"] = self.engine.bounds.t_exposure_2

                if self.model_function != self.engine.models.expo_buri_expo:
                    bounds["t_burial_2"] = self.engine.bounds.t_burial_2

        self.fit_runner = FitRunner(self.engine, self.x_data,
            self.y_data, self.y_err_std, self.model_function, known_params,
            bounds, fit_type, known_params_err_std=known_params_err_std,
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
                split_param_name = param_name.split("_")
                histo_title = "$" + split_param_name[0] + r"_{\mathrm{" \
                    + split_param_name[1] + "}, " \
                    + split_param_name[2] + "}$"
                self.ui.result_table.set_posterior_samples(param_name, samples,
                    histo_title)

        # construct known params
        known_params = {"order": self.order, "sigma_phi": self.sigma_phi,
            "mu": self.mu}
        if self.model_function != self.engine.models.expo:
            known_params["f"] = self.f
        # plot fitted curve
        x_data_fit = np.linspace(np.min(self.x_data), np.max(self.x_data), 200)
        y_data_fit = self.model_function(x_data_fit, **known_params,
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
