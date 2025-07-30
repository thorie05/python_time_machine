from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Plot(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 4))
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.15)
        self.ax = self.fig.add_subplot(111)
        self.set_axis_labels()
        super().__init__(self.fig)

    def scatter_plot_data(self, x_data, y_data, error=None):
        self.ax.clear()
        self.set_axis_labels()
        if error is not None:
            self.ax.errorbar(x_data, y_data, yerr=error, fmt='o', capsize=4)
        else:
            self.ax.scatter(x_data, y_data)
        self.draw()

    def set_axis_labels(self):
        self.ax.set_xlabel("Depth [mm]")
        self.ax.set_ylabel("Luminescence")
