import pandas as pd

def read_xlsx(filename):
    df = pd.read_excel(filename, engine="openpyxl")

    columns = df.columns.tolist()[:3]
    arrays = []

    for col in columns:
        arrays.append(df[col].to_numpy(dtype=float))

    while len(arrays) < 3:
        arrays.append(None)

    return tuple(arrays)
