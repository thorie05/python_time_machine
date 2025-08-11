from ..shared.standard_widgets import HeaderCell, IndexCell, FloatInput, Table
from ..shared.param_names_unicode import param_names_unicode
from ..shared.param_bounds import param_bounds


class InputParameterTable(Table):
    """Input parameter table widget."""

    def __init__(self, engine):
        # all names result parameter names displayed somewhere int the table
        self.INPUT_PARAMETER_NAMES = ["order", "sigma_phi", "mu", "f"]
        self.DEFAULT_VALUES \
            = {"order": 1.0, "sigma_phi": 5.0, "mu": 5.0, "f": 0.0001}

        bounds_val = param_bounds.val.asdict()
        bounds_std = param_bounds.std.asdict()

        # increment order bounds by 1, see models.py for documentation
        bounds_val["order"] = (bounds_val["order"][0] + 1.0,
            bounds_val["order"][1] + 1.0)

        # dicts mapping parameter names to their table cell widgets
        self.VALUE_INPUT_CELLS = {
            param_name: FloatInput(
            default=self.DEFAULT_VALUES[param_name],
            bounds=bounds_val[param_name]) \
            for param_name in self.INPUT_PARAMETER_NAMES}
        self.STD_INPUT_CELLS = {
            param_name: FloatInput(bounds=bounds_std[param_name]) \
            for param_name in self.INPUT_PARAMETER_NAMES}

        # 2d layout of the table, row by row
        self.LAYOUT = [
            [
                HeaderCell("Input Parameter"),
                HeaderCell("Value"),
                HeaderCell("σ (Standard deviation)"),
            ],
            [
                IndexCell(param_names_unicode.order),
                self.VALUE_INPUT_CELLS["order"],
                self.STD_INPUT_CELLS["order"],
            ],
            [
                IndexCell(param_names_unicode.sigma_phi),
                self.VALUE_INPUT_CELLS["sigma_phi"],
                self.STD_INPUT_CELLS["sigma_phi"],
            ],
            [
                IndexCell(param_names_unicode.mu),
                self.VALUE_INPUT_CELLS["mu"],
                self.STD_INPUT_CELLS["mu"],
            ],
            [
                IndexCell(param_names_unicode.f),
                self.VALUE_INPUT_CELLS["f"],
                self.STD_INPUT_CELLS["f"],
            ],
        ]

        super().__init__(self.LAYOUT)

    def get_value(self, param_name):
        return self.VALUE_INPUT_CELLS[param_name].get_value()

    def get_std(self, param_name):
        return self.STD_INPUT_CELLS[param_name].get_value()
