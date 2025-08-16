from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from PySide6.QtWidgets import QDialog, QVBoxLayout

from .style_config import style_tokens


class HistogramWindow(QDialog):
    """A popup window that displays posterior samples in a histogram."""

    def __init__(self, data, param_name):
        super().__init__()
        self.setObjectName("HistogramWindow")

        self.setWindowTitle(style_tokens.histogram_window.window_title)

        layout = QVBoxLayout()
        self.canvas = FigureCanvasQTAgg(Figure())
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        ax = self.canvas.figure.add_subplot(111)
        ax.clear()
        ax.hist(data, bins="auto", color=style_tokens.plot.histogram_color)
        ax.set_title(f"Posterior distribution of {param_name}")
        ax.set_xlabel("Value")
        ax.set_ylabel("Number of samples")

        self.canvas.draw()


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

        self.x_data_scatter = None
        self.y_data_scatter = None
        self.y_err_data_scatter = None
        self.x_data_plot = None
        self.y_data_plot = None

    def _configure_axis(self):
        """Helper function that sets labels and sets the lower limit to y=0."""

        self.ax.set_xlabel("Depth")
        self.ax.set_ylabel("Luminescence Lx/Tx")
        self.ax.set_ylim(bottom=0)

    def _auto_ylim(self, y_data, y_err):
        """Helper function that sets the limits of y-axis given new data."""

        # set upper limit of the y-axis to show all non-negative data points
        y_upper_limit = np.nanmax(y_data + y_err) * 1.05
        # always start at y=0
        self.ax.set_ylim(bottom=0, top=y_upper_limit)

    def scatter(self, x_data, y_data, y_err_data):
        """
        Plot a scatter of data points with error bars.

        Takes numpy arrays for the x-values, y-values, and y-errors, and
        renders them as a scatter plot with vertical error bars for each point.
        """

        # clear everything, including the previous fitted function plot
        self.clear()

        # assign new scatter data
        self.x_data_scatter = x_data
        self.y_data_scatter = y_data
        self.y_err_data_scatter = y_err_data

        # adjust axis limits and draw
        self.ax.errorbar(self.x_data_scatter, self.y_data_scatter,
            yerr=self.y_err_data_scatter, fmt='o', capsize=4,
            color=style_tokens.plot.scatter_color)
        self._auto_ylim(y_data, y_err_data)
        self.draw()

    def plot(self, x_data, y_data):
        """
        Plot a line graph of the given data.

        Takes numpy arrays for the x-values, y-values and plots a line graph.
        """

        # clear only previous plot, not the scatter
        self.clear_only_plot()

        # store new plot data
        self.x_data_plot = x_data
        self.y_data_plot = y_data

        # adjust axis limits and draw
        self.ax.plot(x_data, y_data, color=style_tokens.plot.plot_color)
        self._auto_ylim(self.y_data_scatter, self.y_err_data_scatter)
        self.draw()

    def clear(self):
        """Clears the entire graph."""

        self.x_data_scatter = None
        self.y_data_scatter = None
        self.y_err_data_scatter = None
        self.x_data_plot = None
        self.y_data_plot = None

        self.ax.cla()
        self._configure_axis()
        self.draw()

    def clear_only_plot(self):
        """Clears only the line graph, not the scatter plot."""

        self.ax.cla()
        self._configure_axis()

        self.x_data_plot = None
        self.y_data_plot = None

        # redraw scatter
        if self.x_data_scatter is not None:
            self._auto_ylim(self.y_data_scatter, self.y_err_data_scatter)
            self.scatter(self.x_data_scatter, self.y_data_scatter,
                self.y_err_data_scatter)

        self.draw()
