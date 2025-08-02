from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Qt, QObject
import numpy as np

from ..shared.fit_runner import FitRunner

from .read_xlsx import read_xlsx
from ..calibration_window.calibration_window import CalibrationWindow


class MainWindowLogic(QObject):
    def __init__(self, main_window, engine):
        super().__init__()
        self.ui = main_window

        self.model_select_options = ["Single Exposure", "Exposure-Burial",
            "Exposure-Burial-Exposure", "Exposure-Burial-Exposure-Burial"]
        self.mcmc_quality_options = ["low", "medium", "high", "very high"]

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

        model_function_select = self.ui.model_select.get_text()
        mcmc_quality = self.ui.quality_select.get_text()

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

        if not (self.engine.bounds.order[0] <= self.order \
            <= self.engine.bounds.order[1]):
            QMessageBox.warning(self.ui, "Warning",
                f"order must lie between {self.engine.bounds.order[0] + 1} "
                f"and {self.engine.bounds.order[1] + 1}.")
            return
        if not (self.engine.bounds.sigma_phi[0] <= self.sigma_phi \
            <= self.engine.bounds.sigma_phi[1]):
            QMessageBox.warning(self.ui, "Warning",
                f"<span style='text-decoration: overline;'>σφ</span>"
                f"<sub>0</sub> must lie between "
                f"{self.engine.bounds.sigma_phi[0]} and "
                f"{self.engine.bounds.sigma_phi[1]}.")
            return
        if not (self.engine.bounds.mu[0] <= self.mu \
            <= self.engine.bounds.mu[1]):
            QMessageBox.warning(self.ui, "Warning",
                f"µ must lie between {self.engine.bounds.mu[0]} and "
                f"{self.engine.bounds.mu[1]}.")
            return

        if fit_type == "mcmc":
            if not (self.engine.bounds.order_std[0] <= self.order_std \
                <= self.engine.bounds.order_std[1]):
                QMessageBox.warning(self.ui, "Warning",
                    f"Standard deviation of order must lie between "
                    f"{self.engine.bounds.order_std[0]} and "
                    f"{self.engine.bounds.order_std[1]}.")
                return

            if not (self.engine.bounds.sigma_phi_std[0] \
                    <= self.sigma_phi_std \
                    <= self.engine.bounds.sigma_phi_std[1]):
                QMessageBox.warning(self.ui, "Warning",
                    f"Standard deviation of <span style='text-decoration: "
                    f"overline;'>σφ</span><sub>0</sub> must lie between "
                    f"{self.engine.bounds.sigma_phi_std[0]} and "
                    f"{self.engine.bounds.sigma_phi_std[1]}.")
                return

            if not (self.engine.bounds.mu_std[0] <= self.mu_std \
                <= self.engine.bounds.mu_std[1]):
                QMessageBox.warning(self.ui, "Warning",
                    f"Standard deviation of µ must lie between "
                    f"{self.engine.bounds.mu_std[0]} and "
                    f"{self.engine.bounds.mu_std[1]}.")
                return


        bounds = {"order": self.engine.bounds.order,
            "sigma_phi": self.engine.bounds.sigma_phi,
            "mu": self.engine.bounds.mu,
            "t_exposure_1": self.engine.bounds.t_exposure_1}

        # select model function
        if model_function_select == self.model_select_options[0]:
            self.model_function = self.engine.models.expo

        else:
            if not (self.engine.bounds.f[0] <= self.f \
                <= self.engine.bounds.f[1]):
                QMessageBox.warning(self.ui, "Warning",
                    f"f must lie between {self.engine.bounds.f[0]} and "
                    f"{self.engine.bounds.f[1]}.")
                return
            if fit_type == "mcmc":
                if not (self.engine.bounds.f_std[0] <= self.f_std \
                    <= self.engine.bounds.f_std[1]):
                    QMessageBox.warning(self.ui, "Warning",
                        f"Standard deviation of f must lie between "
                        f"{self.engine.bounds.f_std[0]} and "
                        f"{self.engine.bounds.f_std[1]}.")
                    return

            known_params["f"] = self.f
            known_params_err_std["f"] = self.f_std
            bounds["t_burial_1"] = self.engine.bounds.t_burial_1

            if model_function_select == self.model_select_options[1]:
                self.model_function = self.engine.models.expo_buri
            else:
                bounds["t_exposure_2"] = self.engine.bounds.t_exposure_2

                if model_function_select == self.model_select_options[2]:
                    self.model_function \
                        = self.engine.models.expo_buri_expo
                else:
                    bounds["t_burial_2"] = self.engine.bounds.t_burial_2

                    self.model_function \
                        = self.engine.models.expo_buri_expo_buri

        self.fit_runner = FitRunner(self.engine, self.x_data,
            self.y_data, self.y_err_std, self.model_function,
            known_params, bounds, fit_type,
            known_params_err_std=known_params_err_std, mcmc_quality=mcmc_quality)

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
        print("a")

        self.ui.progress_bar.setVisible(False)
        self.ui.status_label.setVisible(False)

        print("b")

        result = self.fit_runner.result

        print("c")

        if not result.success:
            QMessageBox.warning(self.ui, "Warning",
                "There have been problems with the fit. The results may be "
                "faulty. Try increasing the fit quality, or improving the "
                "accuracy of the known parameters.")

        bf = result.best_fit
        ci = result.confidence_interval
        ts = result.time_since_events
        if ts is not None:
            ts += [(None, None) for _ in range(4 - len(ts))]
        else:
            ts = [(None, None)] * 4
        ci = {} if ci is None else ci

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

        print(self.t_exposure_1, self.t_exposure_1_confidence_interval)
        print(self.t_burial_1, self.t_burial_1_confidence_interval)
        print(self.t_exposure_2, self.t_exposure_2_confidence_interval)
        print(self.t_burial_2, self.t_burial_2_confidence_interval)

        # set results with confidence intervals
        print("e1")
        self.ui.result_table.set_t_exposure_1(self.t_exposure_1)
        print("e2")
        self.ui.result_table.set_t_exposure_1_confidence_interval(
            self.t_exposure_1_confidence_interval)

        print("e3")
        self.ui.result_table.set_t_burial_1(self.t_burial_1)
        print("e4")
        self.ui.result_table.set_t_burial_1_confidence_interval(
            self.t_burial_1_confidence_interval)

        print("e5")
        self.ui.result_table.set_t_exposure_2(self.t_exposure_2)
        print("e6")
        self.ui.result_table.set_t_exposure_2_confidence_interval(
            self.t_exposure_2_confidence_interval)

        print("e7")
        self.ui.result_table.set_t_burial_2(self.t_burial_2)
        print("e8")
        self.ui.result_table.set_t_burial_2_confidence_interval(
            self.t_burial_2_confidence_interval)

        # set time since results with confidence intervals
        print("e9")
        self.ui.result_table.set_t_since_exposure_1(self.t_since_exposure_1)
        print("e10")
        self.ui.result_table.set_t_since_exposure_1_confidence_interval(
            self.t_since_exposure_1_confidence_intervals)

        print("e11")
        self.ui.result_table.set_t_since_burial_1(self.t_since_burial_1)
        print("e12")
        self.ui.result_table.set_t_since_burial_1_confidence_interval(
            self.t_since_burial_1_confidence_intervals)

        print("e13")
        self.ui.result_table.set_t_since_exposure_2(self.t_since_exposure_2)
        print("e14")
        self.ui.result_table.set_t_since_exposure_2_confidence_interval(
            self.t_since_exposure_2_confidence_intervals)

        print("e15")
        self.ui.result_table.set_t_since_burial_2(self.t_since_burial_2)
        print("e16")
        self.ui.result_table.set_t_since_burial_2_confidence_interval(
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

        self.ui.plot_widget.plot(x_data_fit, y_data_fit)

        print("i")

        self.fit_runner = None

        print("j")

    def on_fit_failed(self, message):
        self.ui.progress_bar.setVisible(False)
        self.ui.status_label.setVisible(False)
        QMessageBox.critical(self.ui, "Error",
            "Fit crashed. This should not happen. Could be caused by bad input "
            f"data or bad input parameters. \n\nError message: \n{message}")

    def clear_fit_runner(self):
        self.fit_runner = None
