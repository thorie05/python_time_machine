from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFileDialog

from .style_config import style_tokens
from .basic_widgets import Button


class HistogramWindow(QDialog):
    """A popup window that displays posterior samples in a histogram."""

    def __init__(self, data, param_name, parent=None):
        super().__init__(parent)
        self.setObjectName("HistogramWindow")

        self.data = data
        self.param_name = param_name

        self.setWindowTitle(style_tokens.histogram_window.window_title)

        layout = QVBoxLayout(self)

        self.canvas = FigureCanvasQTAgg(Figure())
        layout.addWidget(self.canvas)

        button_layout = QHBoxLayout()

        self.save_button = Button("Save PNG")
        self.save_button.clicked.connect(self.save_png)

        self.action_button = Button("Save CSV")
        self.action_button.clicked.connect(self.save_csv)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.action_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        ax = self.canvas.figure.add_subplot(111)
        ax.clear()
        ax.hist(self.data, bins="auto", color=style_tokens.plot.histogram_color)
        ax.set_title(f"Posterior distribution of {self.param_name}")
        ax.set_xlabel("Value")
        ax.set_ylabel("Number of samples")

        self.canvas.draw()

    def save_png(self):
        """Saves the histogram as a png file."""

        filename, _ = QFileDialog.getSaveFileName(self, "Save histogram", "",
            "PNG Images (*.png)")
        if filename:
            if not filename.lower().endswith(".png"):
                filename += ".png"

            self.canvas.figure.savefig(filename, dpi=300, bbox_inches="tight")

    def save_csv(self):
        """Saves the histogram data as a CSV file."""

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save data", "", "CSV File (*.csv)")

        if filename:
            if not filename.lower().endswith(".csv"):
                filename += ".csv"

            with open(filename, "w", newline="", encoding="utf-8") as file:
                file.write(f"{self.param_name}\n")
                file.write(",".join(map(str, self.data)) + "\n")


class Plot(FigureCanvasQTAgg):
    """
    A Plot widget using matplotlib.

    Supports scattering datapoints with y-errors as well as plotting the fitted
    function. The graph always starts at y=0.
    """

    def __init__(self):
        self.fig = Figure(figsize=(5, 4))
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.15)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self._configure_axis()

        self.setMinimumWidth(style_tokens.plot.minimum_width)
        self.setMinimumHeight(style_tokens.plot.minimum_height)

        self.x_data_scatter = []
        self.y_data_scatter = []
        self.y_err_data_scatter = []
        self.name_data_scatter = []
        self.color_data_scatter = []

    def _configure_axis(self):
        """Helper function that sets labels and sets the lower limit to y=0."""

        self.ax.set_xlabel("Depth")
        self.ax.set_ylabel("Luminescence Lx/Tx")
        self.ax.set_ylim(bottom=0)

    def _auto_ylim(self):
        """Helper function that sets the limits of y-axis given new data."""

        # set upper limit of the y-axis to show all non-negative data points
        y_upper_limit = 0
        for y_data, y_err in zip(self.y_data_scatter, self.y_err_data_scatter):
            y_upper_limit = max(np.nanmax(y_data + y_err) * 1.05, y_upper_limit)

        # always start at y=0
        self.ax.set_ylim(bottom=0, top=y_upper_limit)

    def scatter(self, x_data, y_data, y_err_data, name=None, color=None):
        """
        Plot a scatter of data points with error bars.

        Takes numpy arrays for the x-values, y-values, and y-errors, and
        renders them as a scatter plot with vertical error bars for each point.
        """

        # assign new scatter data
        self.x_data_scatter.append(x_data)
        self.y_data_scatter.append(y_data)
        self.y_err_data_scatter.append(y_err_data)
        self.name_data_scatter.append(name)
        self.color_data_scatter.append(color)

        # adjust axis limits and draw
        self.ax.errorbar(x_data, y_data, yerr=y_err_data, fmt='o', capsize=4,
            color=color, label=name)

        if len(self.x_data_scatter) > 1:
            self.ax.legend()

        self._auto_ylim()
        self.draw()

    def plot(self, x_data, y_data, color=None):
        """
        Plot a line graph of the given data.

        Takes numpy arrays for the x-values, y-values and plots a line graph.
        """

        self.ax.plot(x_data, y_data, color=color)
        self.draw()

    def clear(self):
        """Clears the entire graph."""

        self.x_data_scatter.clear()
        self.y_data_scatter.clear()
        self.y_err_data_scatter.clear()
        self.name_data_scatter.clear()
        self.color_data_scatter.clear()

        self.ax.cla()
        self._configure_axis()
        self.draw()

    def clear_only_plot(self):
        """Clears only the line graph, not the scatter plot."""

        self.ax.cla()
        self._configure_axis()

        # redraw all scatters
        for x_data, y_data, y_err_data, name, color in \
            zip(self.x_data_scatter, self.y_data_scatter,
            self.y_err_data_scatter, self.name_data_scatter,
            self.color_data_scatter):

            self.ax.errorbar(x_data, y_data, yerr=y_err_data, fmt='o',
                capsize=4, color=color, label=name)

        if len(self.x_data_scatter) > 1:
            self.ax.legend()

        self._auto_ylim()
        self.draw()
