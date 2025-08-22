from ..shared.table import (
    ClickableContentCell,
    HeaderCell,
    IndexCell,
    InputCell,
    Table
)


class CalibrationSamplesTable(Table):
    """Table widgets that shows loaded samples with t_exposure input cells."""

    def __init__(self):
        self.input_cells = None 

        self.header_row = [
            HeaderCell("Sample name"),
            HeaderCell("Exposure Time"),
        ]

        # show one blank row after the header when no samples are loaded
        self.table_layout = [
            self.header_row,
            [IndexCell(), ClickableContentCell()]
        ]

        super().__init__(self.table_layout, 2)

    def update_calibration_samples(self, calibration_sample_names):
        """Updates the calibration samples table with new samples."""

        # update the input cells
        self.input_cells = {sample_name: InputCell() \
            for sample_name in calibration_sample_names}

        # update table layout
        self.table_layout = [self.header_row]
        for sample_name, input_cell in self.input_cells.items():
            self.table_layout.append([IndexCell(sample_name), input_cell])

        # add invisble ghost rows if there are less than 3 samples to match the
        # table layout to the calibration parameter table
        self.ghost_rows = max(0, 4 - len(self.table_layout))

        self.update_layout()

    def get_value(self, sample_name):
        """Returns the current value for the exposure time of a given sample."""

        if self.input_cells is not None:
            return self.input_cells[sample_name].get_value()
        return None
