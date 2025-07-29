from fitting_engine import Calibrator
import numpy as np
import matplotlib.pyplot as plt
from fitting_engine import models

rng = np.random.default_rng()

order = 0.0
f = 0.0001

true_sigma_phi = 5
true_mu = 5

results_sigma_phi = [[]]
results_sigma_phi_std = [[]]
results_mu = [[]]
results_mu_std = [[]]

cal = Calibrator(order, 0.0, fit_quality="low")

max_num_of_samples = 10

for k in range(1, max_num_of_samples + 1):
    results_sigma_phi.append([])
    results_sigma_phi_std.append([])
    results_mu.append([])
    results_mu_std.append([])
    for j in range(500):
        print(k, j)
        t_exposure_list = [1000] * k
        x_data_list = []
        y_data_list = []
        y_err_std_list = []

        for i, t_exposure in enumerate(t_exposure_list):
            x_data_list.append(np.linspace(0, 3, 30))
            y_data_list.append(models.expo(x_data_list[i], order,
                true_sigma_phi, true_mu, t_exposure))
            perturbation = np.random.normal(loc=0.0, scale=0.05,
                size=x_data_list[i].shape)

            y_data_list[i] = y_data_list[i] + perturbation
            y_data_list[i] = np.maximum(y_data_list[i], 0)
            y_err_std_list.append(np.full(len(x_data_list[0]), 0.05))

        for i, t_exposure in enumerate(t_exposure_list):
            cal.add_calibration(t_exposure, x_data_list[i], y_data_list[i],
                y_err_std_list[i])

        results_sigma_phi[k].append(cal.sigma_phi)
        results_sigma_phi_std[k].append(cal.sigma_phi_std)
        results_mu[k].append(cal.mu)
        results_mu_std[k].append(cal.mu_std)

        cal.clear_calibrations()

print(results_sigma_phi)
print(results_sigma_phi_std)
print(results_mu)
print(results_mu_std)

for i in range(1, max_num_of_samples + 1):
    print(i)
    print("sigma_phi", np.mean(results_sigma_phi[i]))
    print("sigma_phi_std", np.mean(results_sigma_phi_std[i]))
    print("mu", np.mean(results_mu[i]))
    print("mu_std", np.mean(results_mu_std[i]))
    print()
