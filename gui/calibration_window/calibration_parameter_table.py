from ..shared.table import (
    ClickableContentCell,
    HeaderCell,
    IndexCell,
    InputCell,
    Table,
)
from ..shared.style_config import param_names_unicode


class CalibrationParameterTable(Table):
    """
    Table widget that displays calibration results.

    ...
    """

    def __init__(self, engine):
        # dicts mapping parameter names to their table cell widgets

        # retrieve value and std bounds from the engine
        # increment order bounds by 1, see fitting engine models
        bounds_val_order = (engine.param_bounds.val.order[0] + 1.0,
            engine.param_bounds.val.order[1] + 1.0)
        bounds_std_order = engine.param_bounds.std.order

        self.sigma_phi_cell = ClickableContentCell()
        self.sigma_phi_std_cell = ClickableContentCell()
        self.mu_cell = ClickableContentCell()
        self.mu_std_cell = ClickableContentCell()
        self.order_cell = InputCell(default=1.0, bounds=bounds_val_order)
        self.order_std_cell = InputCell(bounds=bounds_std_order)

        # 2d layout of the table, row by row
        self.table_layout = [
            [
                HeaderCell("Parameter name"),
                HeaderCell("Value"),
                HeaderCell("σ (Standard deviation)"),
            ],
            [
                IndexCell(param_names_unicode.order + "  (Input)"),
                self.order_cell,
                self.order_std_cell
            ],
            [
                IndexCell(param_names_unicode.sigma_phi + "  (Result)"),
                self.sigma_phi_cell,
                self.sigma_phi_std_cell
            ],
            [
                IndexCell(param_names_unicode.mu + "  (Result)"),
                self.mu_cell,
                self.mu_std_cell
            ]
        ]

        super().__init__(self.table_layout)

        # always round to two digits
        self.ROUND_TO_DIGITS = 6

    def clear(self):
        """Clears all result cells in the table."""

        self.sigma_phi_cell.setText("")
        self.sigma_phi_cell.disconnect_double_click()
        self.sigma_phi_std_cell.setText("")

        self.mu_cell.setText("")
        self.mu_cell.disconnect_double_click()
        self.mu_std_cell.setText("")

    def get_order(self):
        return self.order_cell.get_value()

    def get_order_std(self):
        return self.order_std_cell.get_value()

    def set_sigma_phi(self, value):
        self._set_value(self.sigma_phi_cell, value)

    def set_sigma_phi_std(self, value):
        self._set_value(self.sigma_phi_std_cell, value)

    def set_mu(self, value):
        self._set_value(self.mu_cell, value)

    def set_mu_std(self, value):
        self._set_value(self.mu_std_cell, value)

    def _set_value(self, cell, value):
        label_text = ""
        if value is not None:
            label_text = f"{round(value, self.ROUND_TO_DIGITS)}"
        cell.setText(label_text)
