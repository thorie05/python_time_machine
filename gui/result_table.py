from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy, QFrame
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt

from gui.ui_style import ui_style

class ResultTable(QWidget):
    """Results table widget."""

    def __init__(self):
        super().__init__()

        # exposure 1
        self.t_exposure_1 = None
        self.t_exposure_1_lower = None
        self.t_exposure_1_upper = None
        self.t_since_exposure_1 = None
        self.t_since_exposure_1_lower = None
        self.t_since_exposure_1_upper = None

        # burial 1
        self.t_burial_1 = None
        self.t_burial_1_lower = None
        self.t_burial_1_upper = None
        self.t_since_burial_1 = None
        self.t_since_burial_1_lower = None
        self.t_since_burial_1_upper = None

        # exposure 2
        self.t_exposure_2 = None
        self.t_exposure_2_lower = None
        self.t_exposure_2_upper = None
        self.t_since_exposure_2 = None
        self.t_since_exposure_2_lower = None
        self.t_since_exposure_2_upper = None

        # burial 2
        self.t_burial_2 = None
        self.t_burial_2_lower = None
        self.t_burial_2_upper = None
        self.t_since_burial_2 = None
        self.t_since_burial_2_lower = None
        self.t_since_burial_2_upper = None

        # create main grid layout
        self.grid = QGridLayout()
        self.grid.setSpacing(0)  # no spacing between cells
        self.grid.setContentsMargins(0, 0, 0, 0)
        
        # header labels
        headers = ["Parameter", "Result", "95% Confidence Range",
            "Time since", "Result", "95% Confidence Range"]

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

        def fmt(value, decimals=4):
            """Format helper function"""
            return "" if value is None else f"{round(value, decimals)}"

        column_0 = [
            "t<sub>exposure,1</sub>",
            "t<sub>burial,1</sub>",
            "t<sub>exposure,2</sub>",
            "t<sub>burial,2</sub>"
        ]

        column_1 = [
            f"{fmt(self.t_exposure_1)}",
            f"{fmt(self.t_burial_1)}",
            f"{fmt(self.t_exposure_2)}",
            f"{fmt(self.t_burial_2)}"
        ]

        column_2 = [
            f"{fmt(self.t_exposure_1_lower)} - "
            f"{fmt(self.t_exposure_1_upper)}",
            f"{fmt(self.t_burial_1_lower)} - "
            f"{fmt(self.t_burial_1_upper)}",
            f"{fmt(self.t_exposure_2_lower)} - "
            f"{fmt(self.t_exposure_2_upper)}",
            f"{fmt(self.t_burial_2_lower)} - "
            f"{fmt(self.t_burial_2_upper)}",
        ]

        column_3 = [
            "exposure 1",
            "burial 1",
            "exposure 2",
            "burial 2"
        ]

        column_4 = [
            f"{fmt(self.t_since_exposure_1)}",
            f"{fmt(self.t_since_burial_1)}",
            f"{fmt(self.t_since_exposure_2)}",
            f"{fmt(self.t_since_burial_2)}"
        ]

        column_5 = [
            f"{fmt(self.t_since_exposure_1_lower)} - "
            f"{fmt(self.t_since_exposure_1_upper)}",
            f"{fmt(self.t_since_burial_1_lower)} - "
            f"{fmt(self.t_since_burial_1_upper)}",
            f"{fmt(self.t_since_exposure_2_lower)} - "
            f"{fmt(self.t_since_exposure_2_upper)}",
            f"{fmt(self.t_since_burial_2_lower)} - "
            f"{fmt(self.t_since_burial_2_upper)}",
        ]


        # add index columns
        index_cols = [(0, column_0), (3, column_3)]
        for col_number, col in index_cols:
            for row_number, text in enumerate(col, start=1):
                label = QLabel(text)
                label.setStyleSheet(
                    "background-color: "
                    f"{ui_style.table.index_background_color};"
                    f"border: {ui_style.table.border_width}px solid "
                    f"{ui_style.table.border_color};"
                    f"padding: {ui_style.table.cell_padding}px;"
                )
                label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                label.setTextFormat(Qt.RichText)
                label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.grid.addWidget(label, row_number, col_number)

        # add value columns
        value_cols = [(1, column_1), (2, column_2), (4, column_4),
            (5, column_5)]
        for col_number, col in value_cols:
            for row_number, text in enumerate(col, start=1):
                label = QLabel(text)
                label.setStyleSheet(
                    "background-color: "
                    f"{ui_style.table.cell_background_color};"
                    f"border: {ui_style.table.border_width}px solid "
                    f"{ui_style.table.border_color};"
                    f"padding: {ui_style.table.cell_padding}px;"
                )
                label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                label.setTextFormat(Qt.RichText)
                label.setCursor(Qt.IBeamCursor)
                label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.grid.addWidget(label, row_number, col_number)

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
