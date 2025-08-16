from pathlib import Path

from openpyxl import Workbook
import pandas as pd


def read_xlsx(path):
    """Reads a .xlsx luminescence data file."""
    dfs = pd.read_excel(path, sheet_name=None, engine="openpyxl")

    result = {}
    for sheet_name, df in dfs.items():
        columns = df.columns.tolist()[:3]
        arrays = []

        for col in columns:
            arrays.append(df[col].to_numpy(dtype=float))

        while len(arrays) < 3:
            arrays.append(None)

        result[sheet_name] = tuple(arrays)

    return result


def write_xlsx(path):
    p = Path(path)

    wb = Workbook()
    ws = wb.active

    ws["A1"] = "Fit Export"
    p.parent.mkdir(parents=True, exist_ok=True)
    wb.save(p.as_posix())
