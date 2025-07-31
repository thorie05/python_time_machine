from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from gui.ui_style import ui_style


class Plot(FigureCanvas):
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
        self.ax.set_xlabel("Depth [mm]")
        self.ax.set_ylabel("Luminescence Lx/Tx")
        self.ax.set_ylim(bottom=0)

    def scatter(self, x_data, y_data, y_err_data=None):
        # if new scatter plot clear everything
        self.clear()

        # take new scatter data
        self.x_data_scatter = x_data
        self.y_data_scatter = y_data
        self.y_err_data_scatter = y_err_data

        # draw scatter
        self._draw_scatter()

        # adjust limits
        self._auto_ylim(y_data, y_err_data)
        self.draw()

    def plot(self, x_data, y_data):
        # clear only axes (not data)
        self.clear()

        # re-draw scatter if available
        if self.x_data_scatter is not None:
            self._draw_scatter()

        # take new plot data
        self.x_data_plot = x_data
        self.y_data_plot = y_data

        # show new plot
        self.ax.plot(x_data, y_data, color=ui_style.plot.plot_color)

        # adjust limits
        self._auto_ylim(self.y_data_scatter, self.y_err_data_scatter)
        self.draw()

    def _draw_scatter(self):
        if self.x_data_scatter is not None and self.y_data_scatter is not None:
            if self.y_err_data_scatter is not None:
                self.ax.errorbar(self.x_data_scatter, self.y_data_scatter,
                    yerr=self.y_err_data_scatter, fmt='o', capsize=4,
                    color=ui_style.plot.scatter_color)
            else:
                self.ax.scatter(self.x_data_scatter, self.y_data_scatter,
                    color=ui_style.plot.scatter_color)

    def clear(self):
        self.ax.cla()
        self._configure_axis()
        self.draw()

    def _auto_ylim(self, y_data, y_err=None):
        y_data = np.asarray(y_data)
        if y_err is not None:
            y_err = np.asarray(y_err)
            y_max = np.nanmax(y_data + y_err)
        else:
            y_max = np.nanmax(y_data)

        if not np.isfinite(y_max) or y_max <= 0:
            y_max = 1

        self.ax.set_ylim(bottom=0, top=y_max * 1.05)

