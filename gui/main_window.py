from PySide6.QtWidgets import QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QComboBox, QLayout
from PySide6.QtCore import Qt

from gui.calibration_window import CalibrationWindow
from gui.input_parameter_table import InputParameterTable
from gui.result_table import ResultTable
from gui.plot import Plot
from gui.standard_button import StandardButton
from gui.read_xslx import read_xlsx
from gui.ui_style import ui_style


class MainWindow(QWidget):
    def __init__(self, engine):
        super().__init__()

        # create window
        self.setWindowTitle("Python Time Machine")
        self.resize(ui_style.main_window.default_width,
            ui_style.main_window.default_height)

        # calibration window
        self.calibration_window = None

        # set background color for main window
        self.setStyleSheet(
            f"background-color: {ui_style.main_window.background_color};")

        # outer layout
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(ui_style.main_window.outer_margin,
            ui_style.main_window.outer_margin,
            ui_style.main_window.outer_margin, 0)
        outer_layout.setSpacing(ui_style.main_window.inner_window_spacing)

        # set headline
        headline = QLabel("Python Time Machine")
        headline.setStyleSheet(f"font-size: {ui_style.headline1.font_size}px; "
            f"font-weight: {ui_style.headline1.font_weight};")
        headline.setAlignment(Qt.AlignLeft)
        outer_layout.addWidget(headline)

        # content area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # top row with input parameter table and result table widgets
        top_row = QHBoxLayout()
        top_row.addWidget(InputParameterTable(engine))
        top_row.addWidget(ResultTable())
        content_layout.addLayout(top_row, stretch=1)

        # bottom row with plot widget and buttons
        bottom_row = QHBoxLayout()
        self.plot_widget = Plot()
        bottom_row.addWidget(self.plot_widget, stretch=4)

        # button column
        button_column = QVBoxLayout()
        button_column.setSpacing(15) 
        button_column.setContentsMargins(0, 50, 0, 0)

        # calibration button
        calibration_button = StandardButton("Calibrate")
        calibration_button.clicked.connect(self.open_calibration_window)
        button_column.addWidget(calibration_button)

        # load .xslx button
        load_button = StandardButton("Choose .xlsx data")
        load_button.clicked.connect(self.load_and_plot_xlsx)
        button_column.addWidget(load_button)

        # combo box for model selection

        model_select_widget = QWidget()
        model_select_layout = QVBoxLayout(model_select_widget)
        model_select_layout.setContentsMargins(0, 0, 0, 0)
        model_select_layout.setSpacing(0) 

        model_select_layout.setSizeConstraint(QLayout.SetFixedSize)

        # Label
        model_select_label = QLabel("Select model:")

        # ComboBox
        model_select_combo = QComboBox()
        model_select_combo.addItems(["Single Exposure", "Exposure-Burial",
            "Exposure-Burial-Exposure", "Exposure-Burial-Exposure-Burial"])

        model_select_layout.addWidget(model_select_label)
        model_select_layout.addWidget(model_select_combo)
        button_column.addWidget(model_select_widget)
        button_column.addStretch(1)

        # button column widget
        button_column_widget = QWidget()
        button_column_widget.setLayout(button_column)
        bottom_row.addWidget(button_column_widget, stretch=1) 

        content_layout.addLayout(bottom_row, stretch=3)

        # add stretchable content layout
        outer_layout.addLayout(content_layout, 1)

        self.setLayout(outer_layout)

    def load_and_plot_xlsx(self):
        """Opens a file dialog to open the data and plots them on the screen."""

        filename, _ = QFileDialog.getOpenFileName(self, "Open .xlsx File",
            "", "Excel Files (*.xlsx);;All Files (*)")
        if filename:
            x_data, y_data, y_err_std = read_xlsx(filename)
            self.plot_widget.scatter_plot_data(x_data, y_data, error=y_err_std)

    def open_calibration_window(self):
        if self.calibration_window is None or not self.calibration_window.isVisible():
            self.calibration_window = CalibrationWindow()
            self.calibration_window.show()
        else:
            self.calibration_window.raise_()
            self.calibration_window.activateWindow()
