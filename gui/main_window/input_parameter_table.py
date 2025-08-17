from ..shared.table import HeaderCell, IndexCell, InputCell, Table
from ..shared.style_config import param_names_unicode


class InputParameterTable(Table):
    """
    Table widget for entering model input parameters.

    A table exposing input fields for the relevant input parameters (order,
    sigma_phi, mu and f), along with their standard deviations.
    """

    def __init__(self, engine):
        # all names result parameter names displayed somewhere int the table
        self.INPUT_PARAMETER_NAMES = ["order", "sigma_phi", "mu", "f"]
        self.INPUT_PARAMETER_DEFAULT_VALUES \
            = {"order": 1.0, "sigma_phi": 5.0, "mu": 5.0, "f": 0.0001}

        # retrieve value and std bounds from the engine
        bounds_val = engine.param_bounds.val.asdict()
        bounds_std = engine.param_bounds.std.asdict()

        # increment order bounds by 1, see fitting engine models
        bounds_val["order"] = (bounds_val["order"][0] + 1.0,
            bounds_val["order"][1] + 1.0)

        # dicts mapping parameter names to their table input cell widgets
        self.VALUE_INPUT_CELLS = {
            param_name: InputCell(
            default=self.INPUT_PARAMETER_DEFAULT_VALUES[param_name],
            bounds=bounds_val[param_name]) \
            for param_name in self.INPUT_PARAMETER_NAMES}
        self.STD_INPUT_CELLS = {
            param_name: InputCell(bounds=bounds_std[param_name]) \
            for param_name in self.INPUT_PARAMETER_NAMES}

        # 2d layout of the table, row by row
        self.table_layout = [
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

        super().__init__(self.table_layout)

    def get_value(self, param_name):
        """Returns the current value for a given parameter."""

        return self.VALUE_INPUT_CELLS[param_name].get_value()

    def get_std(self, param_name):
        """Returns the current standard deviation for a given parameter."""

        return self.STD_INPUT_CELLS[param_name].get_value()
