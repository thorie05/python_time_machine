from fitting_engine import easy_fit
from fitting_engine.models import expo
import numpy as np
import matplotlib.pyplot as plt

def perturb(y_data, scale):
    perturbation = np.random.normal(loc=0.0, scale=scale, size=y_data.shape)
    return y_data + perturbation

order = 1.0
mu = 5

true_sigma_phi = 5

t_exposure = 100

x_data = np.linspace(0, 3, 35)

scale = 0.05

y_data = expo(x_data, order, true_sigma_phi, mu, t_exposure)

y_data_1 = perturb(y_data, scale)
y_data_1 = np.clip(y_data_1, 0, 1)

y_data_2 = perturb(y_data, scale)
y_data_2 = np.clip(y_data_2, 0, 1)

y_data_3 = perturb(y_data, scale)
y_data_3 = np.clip(y_data_3, 0, 1)

fit_result_1 = easy_fit(x_data, y_data_1, expo, {"order": order,
    "t_exposure_1": t_exposure, "mu": mu}, {"sigma_phi": 5}, only_positive=True)
sigma_phi_fit_1 = fit_result_1.best_fit["sigma_phi"]

fit_result_2 = easy_fit(x_data, y_data_2, expo, {"order": order,
    "t_exposure_1": t_exposure, "mu": mu}, {"sigma_phi": 5}, only_positive=True)
sigma_phi_fit_2 = fit_result_2.best_fit["sigma_phi"]

fit_result_3 = easy_fit(x_data, y_data_3, expo, {"order": order,
    "t_exposure_1": t_exposure, "mu": mu}, {"sigma_phi": 5}, only_positive=True)
sigma_phi_fit_3 = fit_result_3.best_fit["sigma_phi"]

x_data_plot = np.linspace(0, 3, 100)

fit_curve_1 = expo(x_data_plot, order, sigma_phi_fit_1, mu, t_exposure)
fit_curve_2 = expo(x_data_plot, order, sigma_phi_fit_2, mu, t_exposure)
fit_curve_3 = expo(x_data_plot, order, sigma_phi_fit_3, mu, t_exposure)

plt.scatter(x_data, y_data_1, color="red")
plt.plot(x_data_plot, fit_curve_1, color="red",
    label=f"Sigma-Phi: {round(sigma_phi_fit_1, 2)}")
plt.scatter(x_data, y_data_2, color="green")
plt.plot(x_data_plot, fit_curve_2, color="green",
    label=f"Sigma-Phi: {round(sigma_phi_fit_2, 2)}")
plt.scatter(x_data, y_data_3, color="blue")
plt.plot(x_data_plot, fit_curve_3, color="blue",
    label=f"Sigma-Phi: {round(sigma_phi_fit_3, 2)}")
plt.legend()
plt.show()
