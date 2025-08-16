# run with PYTHONPATH=. python tests/create_xlsx_test_data.py

import pandas as pd
import numpy as np
from fitting_engine import models

# true values used for generating the data
n_points = 30
y_err_std = 0.05

order = 0.0
sigma_phi = 5
mu = 5
f = 0.0001

with pd.ExcelWriter("calibration4.xlsx") as writer:
    for i in range(4):
        # true values of the measured sample used for generating the data
        t_exposure_1 = 10 * 10**i

        # generate measurement sample data
        x_data = np.linspace(0, 3, n_points)
        y_data = models.expo(x_data, order, sigma_phi, mu, t_exposure_1)

        # add random perturbation
        perturbation = np.random.normal(
            loc=0.0,
            scale=y_err_std,
            size=y_data.shape
        )
        y_data += perturbation

        # allow only non-zero measurements
        y_data = np.maximum(y_data, 0)

        y_err_std_array = np.full(y_data.shape, y_err_std)

        # create data frame
        df = pd.DataFrame({"Depth": x_data, "Luminescence": y_data,
            "Error": y_err_std_array})

        sheet_name = f"dataset_{i+1}"
        df.to_excel(writer, sheet_name=sheet_name, index=False)
