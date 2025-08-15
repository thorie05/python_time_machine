import pandas as pd


def read_xlsx(filename):
    """
    Reads a .xlsx luminescence data file.

    Reads the contents of the given file. The function expects three columns
    with the first cell of each being the header description. The first column
    should contain the x-data (depth in the rock), the second the y-data (Lx/Tx)
    and the third the y-errors (1 standard deviation).
    """

    df = pd.read_excel(filename, engine="openpyxl")

    columns = df.columns.tolist()[:3]
    arrays = []

    for col in columns:
        arrays.append(df[col].to_numpy(dtype=float))

    while len(arrays) < 3:
        arrays.append(None)

    return tuple(arrays)
