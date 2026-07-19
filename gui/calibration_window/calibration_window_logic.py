from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox
import numpy as np

from ..shared.basic_widgets import MessageBoxFitCrash
from ..shared.fit_runner import FitRunner
from ..shared.read_write_xlsx import read_xlsx, write_xlsx
from ..shared.style_config import param_names_unicode, style_tokens


class CalibrationWindowLogic(QObject):
    def __init__(self, calibration_window, engine,
        apply_calibration_results_main_window_func):
        super().__init__()

        # store calibration window class to access ui elements
        self.ui = calibration_window

        self.engine = engine
        self.fit_runner = None

        self.apply_calibration_results_main_window_func \
            = apply_calibration_results_main_window_func

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
        self.x_data_dict = {}
        self.y_data_dict = {}
        self.y_err_std_dict = {}
        self.t_exposure_dict = {}
        self.plot_color_dict = {}
        self.order = None
        self.order_std = None
        self.sigma_phi = None
        self.sigma_phi_std = None
        self.mu = None
        self.mu_std = None

        # combined calibration samples
        self.x_data_combined = None
        self.y_data_combined = None
        self.y_err_std_combined = None
        self.t_exposure_combined = None

        # fit results
        self.initial_guess = None
        self.free_params_priors = None
        self.fit_result = None

        # flag depicting whether the fit results are up to date
        self.fit_completed = False

    def load_xlsx(self):
        """Opens a file dialog to open fitting data and plots it."""

        # only allow selecting new data when no fit is running
        if self.fit_runner is not None:
            QMessageBox.warning(self.ui, "Warning",
                "Wait until the current calibration has finished.")
            return

        # open qt file dialog
        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open .xlsx File",
            "", "Excel Files (*.xlsx);;All Files (*)")
        if filename:
            # read xlsx data
            sheet_data = read_xlsx(filename)

            if not sheet_data.keys():
                QMessageBox.warning(self.ui, "Warning", ".xlsx file must "
                "contain at least one data sheet.")
                return

            # check if shapes match
            for sheet_name, (x_data, y_data, y_err_std) in sheet_data.items():
                if not (x_data.shape == y_data.shape == y_err_std.shape):
                    QMessageBox.warning(self.ui, "Warning", ".Each xlsx sheet" \
                    "must consist of three columns of the same height (Depth, "
                    "Lx/Tx and Error).")
                    return

            # set loaded filename
            display_filename = filename.replace("\\", "/").split("/")[-1]
            self.ui.filename_label.setText(display_filename)

            # clear input data dicts
            self.x_data_dict.clear()
            self.y_data_dict.clear()
            self.y_err_std_dict.clear()
            self.t_exposure_dict.clear()
            self.plot_color_dict.clear()

            # clear calibration parameter table results and plot
            self.ui.calibration_parameter_table.clear()
            self.ui.plot_widget.clear()

            # make calibration fit results outdated when new data is loaded
            self.fit_completed = False

            # get number of colors in the color cycle
            num_colors = len(style_tokens.plot.color_cycle)

            for i, sheet_name in enumerate(sheet_data.keys()):
                # fill input data dicts with new data
                self.x_data_dict[sheet_name] = sheet_data[sheet_name][0]
                self.y_data_dict[sheet_name] = sheet_data[sheet_name][1]
                self.y_err_std_dict[sheet_name] = sheet_data[sheet_name][2]

                # cycle through the colors in the plot colors
                color = style_tokens.plot.color_cycle[i % num_colors]

                # if there is only one sample use the single scatter color
                if len(sheet_data.keys()) == 1:
                    color = style_tokens.plot.single_scatter_color
                self.plot_color_dict[sheet_name] = color

                # scatter the new data points 
                self.ui.plot_widget.scatter(self.x_data_dict[sheet_name],
                    self.y_data_dict[sheet_name],
                    self.y_err_std_dict[sheet_name],
                    name=sheet_name, color=color)

            # display the calibration samples in the table
            self.ui.calibration_samples_table.update_calibration_samples(
                list(sheet_data.keys()))

    def apply_calibration_results(self):
        """
        Applies the calibration results.

        Fills the input parameter table in the main window with the calibration
        results and closes the calibration window.
        """

        if self.fit_runner is not None:
            QMessageBox.warning(self.ui, "Warning",
                "Wait until the current calibration has finished.")
            return
        if self.sigma_phi is None:
            QMessageBox.warning(self.ui,
                "Warning", "No calibration fit completed.")
            return

        self.apply_calibration_results_main_window_func(
            self.sigma_phi, self.sigma_phi_std, self.mu, self.mu_std)

        self.ui.close()

    def run_fit(self):
        """Run fit function that is connected to the run fit buttons."""

        if self.fit_runner is not None:
            QMessageBox.warning(self.ui, "Warning", "A fit is already running.")
            return
        if not self.x_data_dict:
            QMessageBox.warning(self.ui, "Warning", "No data loaded.")
            return

        # get order from the calibration parameter table
        self.order = self.ui.calibration_parameter_table.get_order()
        self.order_std = self.ui.calibration_parameter_table.get_order_std()
        # decrement order by 1, see fitting engine models
        self.order -= 1.0

        # get the fit type and quality from the ui combo boxes
        fit_type_select = self.ui.fit_type_select.get_text()
        self.fit_type = self.FIT_TYPE_OPTIONS[fit_type_select]
        fit_quality_select = self.ui.fit_quality_select.get_text()
        self.fit_quality = self.FIT_QUALITY_OPTIONS[fit_quality_select]

        # check that order lies within the allowed bounds
        lower_order, upper_order = self.engine.param_bounds.val.order
        if not (lower_order <= self.order <= upper_order):
            QMessageBox.warning(self.ui, "Warning", 
                f"{param_names_unicode.order} must lie between "
                f"{lower_order + 1} and {upper_order + 1}")
            return

        # get the exposure times for all calibration samples and check that they
        # lie within the allwoed bounds
        lower_t_exposure, upper_t_exposure \
            = self.engine.param_bounds.val.t_exposure_1
        for sample_name in self.x_data_dict:
            t_exposure \
                = self.ui.calibration_samples_table.get_value(sample_name)
            self.t_exposure_dict[sample_name] = t_exposure

            if not (lower_t_exposure <= t_exposure <= upper_t_exposure):
                QMessageBox.warning(self.ui, "Warning", 
                    f"t<sub>exposure</sub> of {sample_name} must lie between "
                    f"{lower_t_exposure} and {upper_t_exposure}")
                return

        # clear result table and previous fitted function
        self.ui.calibration_parameter_table.clear()
        self.ui.plot_widget.clear_only_plot()

        self.ui.progress_bar.setVisible(True)
        self.ui.status_label.setVisible(True)

        # combine individual calibration samples into one large dataset
        self.x_data_combined = np.concatenate(list(self.x_data_dict.values()))
        self.y_data_combined = np.concatenate(list(self.y_data_dict.values()))
        self.y_err_std_combined = np.concatenate(
            list(self.y_err_std_dict.values()))

        # each datapoint gets an individual t_exposure value for the global fit
        self.t_exposure_combined = np.concatenate(
            [np.full(len(arr), t_exposure) for arr, t_exposure in \
            zip(self.x_data_dict.values(), self.t_exposure_dict.values())])

        # order is a scalar that is constant for all datapoints, t_exposure_1 
        # can differ between datapoints because multiple calibration datasets
        # can be used
        self.known_params = {"order": self.order,
            "t_exposure_1": self.t_exposure_combined}
        self.known_params_err_std = {"order": self.order_std}
        self.bounds = {
            "sigma_phi": self.engine.param_bounds.val.sigma_phi,
            "mu": self.engine.param_bounds.val.mu
        }

        # run calibration fit

        self.fit_runner = FitRunner(self.engine, self.x_data_combined,
            self.y_data_combined, self.y_err_std_combined,
            self.engine.models.expo, self.known_params, self.bounds,
            self.fit_type, known_params_err_std=self.known_params_err_std,
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
        """Function that is called when a calibration fit finishes."""

        # save calibration fit results
        self.initial_guess = self.fit_runner.initial_guess
        self.free_params_priors = self.fit_runner.free_params_priors
        self.fit_result = self.fit_runner.fit_result

        # set fit completed flag
        self.fit_completed = True

        # check that the fit results are reliable
        if not self.fit_result.success:
            QMessageBox.warning(self.ui, "Warning",
                "There have been problems with the fit. The results may be "
                "faulty. Try increasing the fit quality, or improving the "
                "accuracy of the known parameters.")

        # hide progres bar and status label
        self.ui.progress_bar.setVisible(False)
        self.ui.status_label.setVisible(False)

        # set fit parameter results in the result table
        result_table = self.ui.calibration_parameter_table
        self.sigma_phi = self.fit_result.best_fit["sigma_phi"]
        self.mu = self.fit_result.best_fit["mu"]
        result_table.set_sigma_phi(self.sigma_phi)
        result_table.set_mu(self.mu)

        # set standard deviations and posterior samples in the result table
        # (only after mcmc fit)
        if self.fit_type == "mcmc":
            self.sigma_phi_std = self.fit_result.std["sigma_phi"]
            self.mu_std = self.fit_result.std["mu"]

            result_table.set_sigma_phi_std(self.sigma_phi_std)
            result_table.set_mu_std(self.mu_std)

            result_table.set_posterior_samples_sigma_phi(
                self.fit_result.samples["sigma_phi"])
            result_table.set_posterior_samples_mu(self.fit_result.samples["mu"])

        # plot fitted curves for each sample
        for sample_name in self.x_data_dict:
            x_data = self.x_data_dict[sample_name]
            t_exposure = self.t_exposure_dict[sample_name]

            x_data_fit = np.linspace(np.min(x_data), np.max(x_data), 200)
            y_data_fit = self.engine.models.expo(x_data_fit,
                self.order, self.sigma_phi, self.mu, t_exposure)

            # use the same color as the scatter data for multiple fits or
            # the default plot color for a single fit
            color = self.plot_color_dict[sample_name]
            if len(self.x_data_dict.keys()) == 1:
                color = style_tokens.plot.single_plot_color

            self.ui.plot_widget.plot(x_data_fit, y_data_fit, color=color)

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
        """Opens a filed dialog to save the fit result datails."""

        if not self.fit_completed or self.fit_type != "mcmc":
            QMessageBox.warning(self.ui, "Warning",
                "No MCMC calibration fit completed.")
            return

        path, _ = QFileDialog.getSaveFileName(self.ui,
            caption="Save fit result as Excel file", dir="",
            filter="Excel Workbook (*.xlsx)")
        if not path:
            return None
        if not path.endswith(".xlsx"):
            path += ".xlsx"

        # add 1 again to order before exporting
        export_known_params = self.known_params.copy()
        export_known_params["order"] += 1

        write_xlsx(path, self.engine.models.expo, self.fit_quality,
            self.x_data_combined, self.y_data_combined, self.y_err_std_combined,
            self.bounds, self.initial_guess, export_known_params,
            self.known_params_err_std, self.free_params_priors,
            self.fit_result.best_fit, self.fit_result.confidence_interval,
            self.fit_result.std, self.fit_result.rmse)
