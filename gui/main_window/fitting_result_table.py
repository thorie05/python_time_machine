from ..shared.plots import HistogramWindow
from ..shared.table import Table, HeaderCell, IndexCell, ClickableContentCell
from ..shared.style_config import param_names_unicode
from functools import partial


class FittingResultTable(Table):
    """
    Table widget that displays fitting results.

    A table displaying the fitting results for the exposure and burial timespans
    and event ages along with their standard deviations.
    """

    def __init__(self):
        # all names result parameter names displayed in the table
        self.RESULT_PARAMETER_NAMES = ["t_exposure_1", "t_burial_1",
            "t_exposure_2", "t_burial_2", "age_exposure_1", "age_burial_1",
            "age_exposure_2", "age_burial_2"]

        # dicts mapping parameter names to their table cell widgets
        self.result_cells = {param_name: ClickableContentCell() \
            for param_name in self.RESULT_PARAMETER_NAMES}
        self.confidence_interval_cells = {param_name: ClickableContentCell() \
            for param_name in self.RESULT_PARAMETER_NAMES}

        # 2d layout of the table, row by row
        self.table_layout = [
            [
                HeaderCell("Parameter"),
                HeaderCell("Result"),
                HeaderCell("95% Confidence Interval"),
                HeaderCell("Event"),
                HeaderCell("Age"),
                HeaderCell("95% Confidence Interval")
            ],
            [
                IndexCell(param_names_unicode.t_exposure_1),
                self.result_cells["t_exposure_1"],
                self.confidence_interval_cells["t_exposure_1"],
                IndexCell("exposure 1"),
                self.result_cells["age_exposure_1"],
                self.confidence_interval_cells["age_exposure_1"],
            ],
            [
                IndexCell(param_names_unicode.t_burial_1),
                self.result_cells["t_burial_1"],
                self.confidence_interval_cells["t_burial_1"],
                IndexCell("burial 1"),
                self.result_cells["age_burial_1"],
                self.confidence_interval_cells["age_burial_1"],
            ],
            [
                IndexCell(param_names_unicode.t_exposure_2),
                self.result_cells["t_exposure_2"],
                self.confidence_interval_cells["t_exposure_2"],
                IndexCell("exposure 2"),
                self.result_cells["age_exposure_2"],
                self.confidence_interval_cells["age_exposure_2"],
            ],
            [
                IndexCell(param_names_unicode.t_burial_2),
                self.result_cells["t_burial_2"],
                self.confidence_interval_cells["t_burial_2"],
                IndexCell("burial 2"),
                self.result_cells["age_burial_2"],
                self.confidence_interval_cells["age_burial_2"],
            ],
        ]

        super().__init__(self.table_layout)

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

    def clear(self):
        """Clears all result cells in the table."""

        for param_name in self.RESULT_PARAMETER_NAMES:
            self.result_cells[param_name].setText("")
            self.result_cells[param_name].disconnect_double_click()
            self.confidence_interval_cells[param_name].setText("")

    def set_posterior_samples(self, param_name, samples):
        """Sets the posterior samples for a given paramter."""

        cell = self.result_cells[param_name]
        if samples is None:
            cell.disconnect_double_click()
        else:
            func = partial(self.show_histogram, samples, param_name)
            cell.connect_double_click(func)

    def show_histogram(self, samples, title):
        """Opens a window with a histogram of the posterior samples."""

        self.histogram_window = HistogramWindow(samples, title)
        self.histogram_window.show()
