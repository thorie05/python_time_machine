from ..shared.histogram_window import HistogramWindow
from ..shared.standard_widgets import Table, HeaderCell, IndexCell, \
    ClickableContentCell
from ..shared.param_names_unicode import param_names_unicode
from functools import partial


class ResultTable(Table):
    """Result table widget."""

    def __init__(self):
        # all names result parameter names displayed somewhere int the table
        self.RESULT_PARAMETER_NAMES = ["t_exposure_1", "t_burial_1",
            "t_exposure_2", "t_burial_2", "age_exposure_1", "age_burial_1",
            "age_exposure_2", "age_burial_2"]

        # dicts mapping parameter names to their table cell widgets
        self.RESULT_CELLS = {param_name: ClickableContentCell() \
            for param_name in self.RESULT_PARAMETER_NAMES}
        self.CONFIDENCE_INTERVAL_CELLS = {param_name: ClickableContentCell() \
            for param_name in self.RESULT_PARAMETER_NAMES}

        # 2d layout of the table, row by row
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
                IndexCell(param_names_unicode.t_exposure_1),
                self.RESULT_CELLS["t_exposure_1"],
                self.CONFIDENCE_INTERVAL_CELLS["t_exposure_1"],
                IndexCell("exposure 1"),
                self.RESULT_CELLS["age_exposure_1"],
                self.CONFIDENCE_INTERVAL_CELLS["age_exposure_1"],
            ],
            [
                IndexCell(param_names_unicode.t_burial_1),
                self.RESULT_CELLS["t_burial_1"],
                self.CONFIDENCE_INTERVAL_CELLS["t_burial_1"],
                IndexCell("burial 1"),
                self.RESULT_CELLS["age_burial_1"],
                self.CONFIDENCE_INTERVAL_CELLS["age_burial_1"],
            ],
            [
                IndexCell(param_names_unicode.t_exposure_2),
                self.RESULT_CELLS["t_exposure_2"],
                self.CONFIDENCE_INTERVAL_CELLS["t_exposure_2"],
                IndexCell("exposure 2"),
                self.RESULT_CELLS["age_exposure_2"],
                self.CONFIDENCE_INTERVAL_CELLS["age_exposure_2"],
            ],
            [
                IndexCell(param_names_unicode.t_burial_2),
                self.RESULT_CELLS["t_burial_2"],
                self.CONFIDENCE_INTERVAL_CELLS["t_burial_2"],
                IndexCell("burial 2"),
                self.RESULT_CELLS["age_burial_2"],
                self.CONFIDENCE_INTERVAL_CELLS["age_burial_2"],
            ],
        ]

        super().__init__(self.LAYOUT)

        # always round to two digits
        self.ROUND_TO_DIGITS = 2

    def set_result(self, param_name, value):
        """Sets the result for a given paramter."""

        #debug:
        print("set result:", param_name, value)

        label_text = ""
        if value is not None:
            label_text = f"{round(value, self.ROUND_TO_DIGITS)}"
        self.RESULT_CELLS[param_name].setText(label_text)

    def set_confidence_interval(self, param_name, interval):
        """Sets the confidence intervals for a given paramter."""

        #debug:
        print("set interval:", param_name, interval)

        label_text = ""
        if interval is not None:
            label_text = f"{round(interval[0], self.ROUND_TO_DIGITS)} - " \
                + f"{round(interval[1], self.ROUND_TO_DIGITS)}"
        self.CONFIDENCE_INTERVAL_CELLS[param_name].setText(label_text)

    def set_posterior_samples(self, param_name, samples):
        """Sets the posterior samples for a given paramter."""
        #debug:
        print("set samples:", param_name)

        cell = self.RESULT_CELLS[param_name]
        if samples is None:
            cell.disconnect_double_click()
        else:
            func = partial(self.show_histogram, samples, param_name)
            cell.connect_double_click(func)

    def clear(self):
        """Clears all result cells in the table."""

        for param_name in self.RESULT_PARAMETER_NAMES:
            self.RESULT_CELLS[param_name].setText("")
            self.RESULT_CELLS[param_name].disconnect_double_click()
            self.CONFIDENCE_INTERVAL_CELLS[param_name].setText("")

    def show_histogram(self, samples, title):
        """Opens a window with a histogram of the posterior samples."""

        self.histogram_window = HistogramWindow(samples, title)
        self.histogram_window.show()
