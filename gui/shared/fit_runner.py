import traceback
from PySide6.QtCore import QObject, QThread, Signal, Slot


class FitRunner(QObject):
    """Fit runner object running all fits."""

    status   = Signal(str) # current status signal displayed in the ui
    finished = Signal()
    failed   = Signal(str)

    def __init__(self, engine, x_data, y_data, y_err_std, model_function,
        known_params, bounds, fit_type, fit_quality, known_params_err_std=None):
        super().__init__()

        self.engine = engine

        # input data
        self.x_data = x_data
        self.y_data = y_data
        self.y_err_std  = y_err_std
        self.model_function = model_function
        self.known_params = known_params
        self.bounds  = bounds
        self.fit_type = fit_type
        self.known_params_err_std = known_params_err_std
        self.fit_quality = fit_quality

        # fit result
        self.initial_guess = None
        self.bootstrap_estimation = None
        self.fit_result = None

        # set up threads
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self.doWork)
        self.finished.connect(self._thread.quit)
        self.failed.connect(self._thread.quit)

        # clean up objects when done
        self._thread.finished.connect(self._thread.deleteLater)
        self.finished.connect(self.deleteLater)
        self.failed.connect(self.deleteLater)

    @Slot()
    def start(self):
        self._thread.start()

    @Slot()
    def doWork(self):
        try:
            if self.fit_type == "mcmc":
                # run full fit
                self.initial_guess, self.bootstrap_estimation, self.fit_result \
                    = self.engine.full_fit(self.x_data, self.y_data,
                    self.y_err_std, self.model_function, self.known_params,
                    known_params_err_std=self.known_params_err_std,
                    bounds=self.bounds, fit_quality=self.fit_quality, cores=1,
                    only_positive=True, status_callback=self.status.emit)
            else:
                # get initial guess
                self.status.emit("Finding initial guess...")

                self.initial_guess = self.engine.get_initial_guess(self.x_data,
                    self.y_data, self.model_function, self.known_params,
                    bounds=self.bounds, y_err_std=self.y_err_std,
                    only_positive=True,
                    num_restarts=self.fit_quality.num_restarts)

                # run least squares
                self.status.emit("Running least-squares fit...")
                self.fit_result = self.engine.easy_fit(self.x_data, self.y_data,
                    self.model_function, self.known_params, self.initial_guess,
                    y_err_std=self.y_err_std)

            self.finished.emit()
        except Exception:
            tb = traceback.format_exc()
            self.failed.emit(tb)
