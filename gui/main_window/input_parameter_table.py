from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QFrame, \
    QSizePolicy
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt

from ..shared.ui_style import ui_style


class InputParameterTable(QWidget):
    """Input parameter table widget."""

    def __init__(self, engine):
        super().__init__()

        # create main grid layout
        self.grid = QGridLayout()
        self.grid.setSpacing(0)  # no spacing between cells
        self.grid.setContentsMargins(0, 0, 0, 0)

        # header labels
        headers = ["Input Parameter", "Value", "σ (Standard deviation)"]
        for col, header in enumerate(headers):
            header_label = QLabel(header)
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet(
                f"background-color: {ui_style.table.header_background_color};"
                f"border: {ui_style.table.border_width} solid "
                f"{ui_style.table.border_color};"
                f"padding: {ui_style.table.cell_padding}px;"
            )
            # header font is bold
            font = header_label.font()
            font.setBold(True)
            header_label.setFont(font)
            self.grid.addWidget(header_label, 0, col)

        # create input fields and labels
        # increase bounds for order by 1 since it's required in the engine
        self.input_order = self._create_float_input(default=1.0,
            bounds=(engine.bounds.order[0] + 1, engine.bounds.order[1] + 1))
        self.input_order_std \
            = self._create_float_input(bounds=engine.bounds.order_std)
        self.input_f = self._create_float_input(bounds=engine.bounds.f)
        self.input_f_std = self._create_float_input(bounds=engine.bounds.f_std)
        self.input_sigma_phi \
            = self._create_float_input(bounds=engine.bounds.sigma_phi)
        self.input_sigma_phi_std \
            = self._create_float_input(bounds=engine.bounds.sigma_phi_std)
        self.input_mu = self._create_float_input(bounds=engine.bounds.mu)
        self.input_mu_std \
            = self._create_float_input(bounds=engine.bounds.mu_std)

        parameter_rows = [
            ("order", self.input_order, self.input_order_std),
            ("F = Ḋ / D₀", self.input_f, self.input_f_std),
            ("<span style='text-decoration: overline;'>σφ</span><sub>0</sub>",
            self.input_sigma_phi, self.input_sigma_phi_std),
            ("μ", self.input_mu, self.input_mu_std),
        ]

        # add parameter rows
        for row, (label_text, value_input, std_input) \
            in enumerate(parameter_rows, start=1):
            label = QLabel(label_text)
            label.setStyleSheet(
                f"background-color: {ui_style.table.index_background_color};"
                f"border: {ui_style.table.border_width}px solid "
                f"{ui_style.table.border_color};"
                f"padding: {ui_style.table.cell_padding}px;"
            )
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.grid.addWidget(label, row, 0)
            self.grid.addWidget(value_input, row, 1)
            self.grid.addWidget(std_input, row, 2)

        # all cells should stretch equally
        for r in range(self.grid.rowCount()):
            self.grid.setRowStretch(r, 1)
        for c in range(self.grid.columnCount()):
            self.grid.setColumnStretch(c, 1)
        
        # create a frame to contain the table for border styling
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Box)
        table_frame.setStyleSheet(
            "QFrame {"
            f"   border: {ui_style.table.border_width}px solid"
            f"{ui_style.table.border_color};"
            "}"
        )
        
        # set layout for the frame
        frame_layout = QGridLayout(table_frame)
        frame_layout.addLayout(self.grid, 0, 0)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        
        # set main layout for the widget
        main_layout = QGridLayout(self)
        main_layout.addWidget(table_frame, 0, 0)
        main_layout.setContentsMargins(5, 0, 5, 0)
    
    def _create_float_input(self, default=0.0, bounds=(0.0, 1_000_000.0)):
        line_edit = QLineEdit(str(default))
        line_edit.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        line_edit.setStyleSheet(
            "QLineEdit {"
            f"   background-color: {ui_style.input.background_color};"
            f"   border: {ui_style.input.border_width}px solid "
            f"{ui_style.input.border_color};"
            f"   padding: {ui_style.input.padding}px;"
            f"   selection-background-color: "
            f"{ui_style.input.selection_background_color};"
            "}"
            "QLineEdit:focus {"
            f"   border: {ui_style.input.border_width}px solid "
            f"{ui_style.input.selection_border_color};"
            "}"
        )

        # validator allows only float input
        validator = QDoubleValidator(bounds[0], bounds[1], 8)
        line_edit.setValidator(validator)
        return line_edit

    # helper function for reading float inputs
    def get_float_value(self, line_edit, default=0.0):
        try:
            return float(line_edit.text())
        except ValueError:
            return default

    # value access methods

    def get_order(self):
        # subtract order by 1 since it's required in the engine
        return self.get_float_value(self.input_order, default=1.0) - 1.0
    
    def get_order_std(self):
        return self.get_float_value(self.input_order_std)
    
    def get_f(self):
        return self.get_float_value(self.input_f)
    
    def get_f_std(self):
        return self.get_float_value(self.input_f_std)
    
    def get_sigma_phi(self):
        return self.get_float_value(self.input_sigma_phi)
    
    def get_sigma_phi_std(self):
        return self.get_float_value(self.input_sigma_phi_std)
    
    def get_mu(self):
        return self.get_float_value(self.input_mu)
    
    def get_mu_std(self):
        return self.get_float_value(self.input_mu_std)
