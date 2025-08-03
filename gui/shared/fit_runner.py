import traceback
from PySide6.QtCore import QObject, QThread, Signal, Slot


class FitRunner(QObject):
    status   = Signal(str)
    finished = Signal()
    failed   = Signal(str)

    def __init__(self, engine, x_data, y_data, y_err_std, model_function,
        known_params, bounds, fit_type, known_params_err_std=None,
        mcmc_quality=None):
        super().__init__()
        self.engine = engine
        self.x_data = x_data
        self.y_data = y_data
        self.y_err_std  = y_err_std
        self.model_function = model_function
        self.known_params = known_params
        self.bounds  = bounds
        self.fit_type = fit_type
        self.known_params_err_std = known_params_err_std
        self.mcmc_quality = mcmc_quality
        self.result = None

        # set up thread
        self._thread = QThread()
        self.moveToThread(self._thread)

        # thread -> worker
        self._thread.started.connect(self.doWork)
        # worker -> thread teardown
        self.finished.connect(self._thread.quit)
        self.failed.connect(self._thread.quit)

        # clean up both objects when done
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
                self.result = self.engine.full_fit(self.x_data, self.y_data,
                    self.y_err_std, self.model_function, self.known_params,
                    known_params_err_std=self.known_params_err_std,
                    bounds=self.bounds, quality=self.mcmc_quality, cores=1,
                    status_callback=self.status.emit)
            else:
                self.status.emit("Finding initial guess...")
                initial_guess = self.engine.get_initial_guess(self.x_data,
                    self.y_data, self.model_function, self.known_params,
                    bounds=self.bounds, y_err_std=self.y_err_std,
                    num_restarts=1)
                self.status.emit("Running least-squares fit...")
                self.result = self.engine.easy_fit(self.x_data, self.y_data,
                    self.model_function, self.known_params, initial_guess,
                    y_err_std=self.y_err_std)
            self.finished.emit()
        except Exception:
            tb = traceback.format_exc()
            self.failed.emit(tb)
