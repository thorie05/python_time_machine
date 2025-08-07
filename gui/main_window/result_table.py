from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy, QFrame
from PySide6.QtCore import Qt
from functools import partial

from ..shared.ui_style import ui_style
from ..shared.standard_widgets import ClickableStandardLabel
from ..shared.histogram_window import HistogramWindow


class ResultTable(QWidget):
    """Results table widget."""

    def __init__(self):
        super().__init__()

        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)

        self.labels = {}
        self.round_to_digits = 2

        self.result_cell_mapping = {
            "t_exposure_1": (1, 1), "t_burial_1": (1, 2),
            "t_exposure_2": (1, 3), "t_burial_2": (1, 4),
            "age_exposure_1": (4, 1), "age_burial_1": (4, 2),
            "age_exposure_2": (4, 3), "age_burial_2": (4, 4)
        }
        self.confidence_interval_cell_mapping = {
            "t_exposure_1": (2, 1), "t_burial_1": (2, 2),
            "t_exposure_2": (2, 3), "t_burial_2": (2, 4),
            "age_exposure_1": (5, 1), "age_burial_1": (5, 2),
            "age_exposure_2": (5, 3), "age_burial_2": (5, 4)}

        headers = ["Parameter", "Result", "95% Confidence Range", "Event",
            "Age (BP)", "95% Confidence Range"]
        for col, header in enumerate(headers):
            header_label = QLabel(header)
            header_label.setAlignment(Qt.AlignVCenter)
            header_label.setStyleSheet(
                f"background-color: {ui_style.table.header_background_color};"
                f"border: {ui_style.table.border_width} solid "
                f"{ui_style.table.border_color};"
                f"padding: {ui_style.table.cell_padding}px;"
            )
            font = header_label.font()
            font.setBold(True)
            header_label.setFont(font)
            self.grid.addWidget(header_label, 0, col)

        column_0 = [
            "t<sub>exposure,1</sub>",
            "t<sub>burial,1</sub>",
            "t<sub>exposure,2</sub>",
            "t<sub>burial,2</sub>"
        ]

        column_3 = [
            "exposure 1",
            "burial 1",
            "exposure 2",
            "burial 2"
        ]

        # index columns
        index_cols = [(0, column_0), (3, column_3)]
        for col_number, col in index_cols:
            for row_number, text in enumerate(col, start=1):
                label = QLabel(text)
                label.setStyleSheet(
                    f"background-color: "
                    f"{ui_style.table.index_background_color};"
                    f"border: {ui_style.table.border_width}px solid "
                    f"{ui_style.table.border_color};"
                    f"padding: {ui_style.table.cell_padding}px;"
                )
                label.setTextFormat(Qt.RichText)
                label.setSizePolicy(QSizePolicy.Expanding,
                    QSizePolicy.Expanding)
                self.grid.addWidget(label, row_number, col_number)

        # empty label placeholders
        for col in [1, 2, 4, 5]:
            for row in range(1, 5):
                label = ClickableStandardLabel("") if col in [1, 4] \
                    else QLabel("")
                label.setStyleSheet(
                    f"background-color: {ui_style.table.cell_background_color};"
                    f"border: {ui_style.table.border_width}px solid "
                    f"{ui_style.table.border_color};"
                    f"padding: {ui_style.table.cell_padding}px;"
                )
                label.setAlignment(Qt.AlignVCenter)
                label.setTextFormat(Qt.RichText)
                label.setCursor(Qt.IBeamCursor)
                label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                label.setSizePolicy(QSizePolicy.Expanding,
                    QSizePolicy.Expanding)
                self.grid.addWidget(label, row, col)
                self.labels[(col, row)] = label

        for r in range(self.grid.rowCount()):
            self.grid.setRowStretch(r, 1)
        for c in range(self.grid.columnCount()):
            self.grid.setColumnStretch(c, 1)

        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Box)
        table_frame.setStyleSheet(
            f"QFrame {{ border: {ui_style.table.border_width}px solid "
            f"{ui_style.table.border_color}; }}"
        )

        frame_layout = QGridLayout(table_frame)
        frame_layout.addLayout(self.grid, 0, 0)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QGridLayout(self)
        main_layout.addWidget(table_frame, 0, 0)
        main_layout.setContentsMargins(5, 0, 5, 0)

    def _update_label(self, col, row, value):
        label = self.labels.get((col, row))
        label_text = ""
        if value is not None:
            label_text = f"{round(value, self.round_to_digits)}"
        label.setText(label_text)

    def _update_conf_label(self, col, row, interval):
        label = self.labels[(col, row)]
        if interval is None:
            label.setText("")
        else:
            lower, upper = interval
            if lower is None or upper is None:
                label.setText("")
            else:
                label.setText(f"{round(lower, self.round_to_digits)} - "
                    f"{round(upper, self.round_to_digits)}")

    def set_result(self, param_name, value):
        print(param_name)
        col, row = self.result_cell_mapping[param_name]
        print(col, row)
        self._update_label(col, row, value)

    def set_confidence_interval(self, param_name, interval):
        col, row = self.confidence_interval_cell_mapping[param_name]
        self._update_conf_label(col, row, interval)

    def set_posterior_samples(self, param_name, samples, hist_title):
        col, row = self.result_cell_mapping[param_name]
        self._connect_labels((col, row), samples, hist_title)

    def _connect_labels(self, pos, samples, param_name):
        # try to first disconnect the previous connection
        try:
            self.labels[pos].doubleClicked.disconnect()
        except TypeError:
            pass  # no existing connection

        if samples is None:
            return

        self.labels[pos].doubleClicked.connect(partial(self.show_histogram,
            samples, param_name))


    def show_histogram(self, samples, param_name):
        self.histogram_window = HistogramWindow(samples, param_name)
        self.histogram_window.show()

    def clear_table(self):
        """Clears all result cells in the table."""

        for (col, _), label in self.labels.items():
            if col in (1, 2, 4, 5):
                label.setText("")
