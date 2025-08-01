import traceback
from PySide6.QtCore import QObject, QThread, Signal, Slot


class FitRunner(QObject):
    status   = Signal(str)
    finished = Signal()
    failed   = Signal(str)

    def __init__(self, engine, x_data, y_data, y_err, model_function,
        known_params, known_params_err_std, bounds, quality):
        super().__init__()
        self.engine = engine
        self.x_data = x_data
        self.y_data = y_data
        self.y_err  = y_err
        self.model_function = model_function
        self.known_params = known_params
        self.known_params_err_std = known_params_err_std
        self.bounds  = bounds
        self.quality = quality
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
            self.result = self.engine.full_fit(self.x_data, self.y_data,
                self.y_err, self.model_function, self.known_params,
                known_params_err_std=self.known_params_err_std,
                bounds=self.bounds, quality=self.quality, cores=1,
                status_callback=self.status.emit)
            self.finished.emit()
        except Exception:
            tb = traceback.format_exc()
            self.failed.emit(tb)
