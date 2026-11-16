import traceback
from PySide6.QtCore import QObject, QThread, Signal, Slot


class FitRunner(QObject):
    """Fit runner object running all fits."""

    status = Signal(str) # current status signal displayed in the ui
    finished = Signal()
    failed = Signal(str)

    def __init__(self, engine, x_data, y_data, y_err_std, model_function,
        known_params_distribution, free_params_bounds, fit_type, fit_quality,
        initial_guess=None):
        super().__init__()

        self.engine = engine

        # input data
        self.x_data = x_data
        self.y_data = y_data
        self.y_err_std  = y_err_std
        self.model_function = model_function
        self.known_params_distribution = known_params_distribution
        self.free_params_bounds = free_params_bounds
        self.fit_type = fit_type
        self.fit_quality = fit_quality

        # fit results
        self.initial_guess = initial_guess
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
            # extract known parameter values
            known_params = {}

            for param_names, distribution in \
                self.known_params_distribution.items():
                if callable(distribution):
                    for name in param_names:
                        known_params[name] = self.initial_guess[name]
                else:
                    known_params[param_names[0]] = distribution[0]

            # get initial guess
            self.status.emit("Finding initial guess...")

            initial_guess = self.engine.get_initial_guess(self.x_data,
                self.y_data, self.model_function, known_params,
                bounds=self.free_params_bounds, y_err_std=self.y_err_std,
                only_positive=True,
                num_restarts=self.fit_quality.num_restarts)

            if self.fit_type == "mcmc":
                # add uncertain known parameters to initial guess
                for param_names, distribution in \
                    self.known_params_distribution.items():
                    if callable(distribution):
                        for name in param_names:
                            initial_guess[name] = self.initial_guess[name]
                    elif distribution[1] != 0:
                        initial_guess[param_names[0]] = distribution[0]

                self.initial_guess = initial_guess

                # run bayesian fit
                self.status.emit("Running Bayesian MCMC fit...")
                self.fit_result = self.engine.bayesian_fit(
                    self.fit_quality.draws, self.fit_quality.tune,
                    self.x_data, self.y_data, self.y_err_std,
                    self.model_function, self.initial_guess,
                    self.free_params_bounds, self.known_params_distribution,
                    only_positive=True)
            else:
                self.initial_guess = initial_guess

                # run least squares
                self.status.emit("Running least-squares fit...")
                self.fit_result = self.engine.easy_fit(self.x_data, self.y_data,
                    self.model_function, known_params, self.initial_guess,
                    y_err_std=self.y_err_std, only_positive=True)

            self.finished.emit()

        except Exception:
            tb = traceback.format_exc()
            self.failed.emit(tb)
