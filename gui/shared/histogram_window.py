from PySide6.QtWidgets import QVBoxLayout, QDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from ..shared.ui_style import ui_style


class HistogramWindow(QDialog):
    def __init__(self, data, param_name):
        super().__init__()
        self.setWindowTitle("Histogram")
        layout = QVBoxLayout()
        self.canvas = FigureCanvasQTAgg(Figure())
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot_histogram(data, param_name)

    def plot_histogram(self, data, param_name):
        ax = self.canvas.figure.add_subplot(111)
        ax.clear()
        ax.hist(data, bins="auto", color=ui_style.plot.histogram_color)
        ax.set_title(f"Posterior distribution of {param_name}")
        ax.set_xlabel("Value")
        ax.set_ylabel("Number of samples")
        self.canvas.draw()