from ..shared.histogram_window import HistogramWindow
from ..shared.standard_widgets import Table, HeaderCell, IndexCell, \
    ClickableContentCell
from functools import partial


class ResultTable(Table):
    """Result table widget."""

    def __init__(self):
        self.RESULT_PARAMETER_NAMES = ["t_exposure_1", "t_burial_1",
            "t_exposure_2", "t_burial_2", "age_exposure_1", "age_burial_1",
            "age_exposure_2", "age_burial_2"]

        self.result_cells = {param_name: ClickableContentCell() \
            for param_name in self.RESULT_PARAMETER_NAMES}

        self.confidence_interval_cells = {param_name: ClickableContentCell() \
            for param_name in self.RESULT_PARAMETER_NAMES}

        self.LAYOUT = [
            [
                HeaderCell("Parameter"),
                HeaderCell("Result"),
                HeaderCell("95% Confidence Interval"),
                HeaderCell("Event"),
                HeaderCell("Age (BP)"),
                HeaderCell("95% Confidence Interval")
            ],
            [
                IndexCell("t<sub>exposure,1</sub>"),
                self.result_cells["t_exposure_1"],
                self.confidence_interval_cells["t_exposure_1"],
                IndexCell("exposure 1"),
                self.result_cells["age_exposure_1"],
                self.confidence_interval_cells["age_exposure_1"],
            ],
            [
                IndexCell("t<sub>burial,1</sub>"),
                self.result_cells["t_burial_1"],
                self.confidence_interval_cells["t_burial_1"],
                IndexCell("burial 1"),
                self.result_cells["age_burial_1"],
                self.confidence_interval_cells["age_burial_1"],
            ],
            [
                IndexCell("t<sub>exposure,2</sub>"),
                self.result_cells["t_exposure_2"],
                self.confidence_interval_cells["t_exposure_2"],
                IndexCell("exposure 2"),
                self.result_cells["age_exposure_2"],
                self.confidence_interval_cells["age_exposure_2"],
            ],
            [
                IndexCell("t<sub>burial,2</sub>"),
                self.result_cells["t_burial_2"],
                self.confidence_interval_cells["t_burial_2"],
                IndexCell("burial 2"),
                self.result_cells["age_burial_2"],
                self.confidence_interval_cells["age_burial_2"],
            ],
        ]

        super().__init__(self.LAYOUT)

        # always round to two digits
        self.ROUND_TO_DIGITS = 2

    def set_result(self, param_name, value):
        """Sets the result for a given paramter."""

        label_text = ""
        if value is not None:
            label_text = f"{round(value, self.ROUND_TO_DIGITS)}"
        self.result_cells[param_name].setText(label_text)

    def set_confidence_interval(self, param_name, interval):
        """Sets the confidence intervals for a given paramter."""

        label_text = ""
        if interval is not None:
            label_text = f"{round(interval[0], self.ROUND_TO_DIGITS)} - " \
                + f"{round(interval[1], self.ROUND_TO_DIGITS)}"
        self.confidence_interval_cells[param_name].setText(label_text)

    def set_posterior_samples(self, param_name, samples):
        """Sets the posterior samples for a given paramter."""

        cell = self.result_cells[param_name]
        if samples is None:
            cell.disconnect_double_click()
        else:
            func = partial(self.show_histogram, samples, param_name)
            cell.connect_double_click(func)

    def clear(self):
        """Clears all result cells in the table."""

        for param_name in self.RESULT_PARAMETER_NAMES:
            self.result_cells[param_name].setText("")
            self.result_cells[param_name].disconnect_double_click()
            self.confidence_interval_cells[param_name].setText("")

    def show_histogram(self, samples, title):
        """Opens a window with a histogram of the posterior samples."""

        self.histogram_window = HistogramWindow(samples, title)
        self.histogram_window.show()
