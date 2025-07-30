import pandas as pd
import numpy as np
from fitting_engine import models

# true values used for generating the data
n_points = 30
true_y_err_std = 0.05

true_order = 0.0
true_sigma_phi = 5
true_mu = 5

# true values of the measured sample used for generating the data
true_t_exposure_1 = 1_000

# generate measuremend sample data
x_data = np.linspace(0, 3, 30)
y_data = models.expo(x_data, true_order, true_sigma_phi, true_mu,
    true_t_exposure_1)
# add random perturbation
perturbation = np.random.normal(loc=0.0, scale=true_y_err_std,
    size=y_data.shape)
y_data += perturbation
# allow only non-zero measurements
y_data = np.maximum(y_data, 0)

y_err_std_array = np.full(y_data.shape, true_y_err_std)

# write to xslx
df = pd.DataFrame({"Depth": x_data, "Luminescence": y_data,
    "Error": y_err_std_array})
df.to_excel("test_data.xlsx", index=False)
