from fitting_engine import easy_fit
from fitting_engine import bootstrap_fit
from fitting_engine import Calibrator
import numpy as np
import matplotlib.pyplot as plt
from fitting_engine import models

rng = np.random.default_rng()

order = 1.0
f = 0.0001

true_sigma_phi = 5
true_mu = 5

n_bootstrap = 10_000
cal = Calibrator(n_bootstrap, order, 5, 5)

n_calibration = 5

t_exposure_list = [5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
x_data_list = []
y_data_list = []

for i in range(n_calibration):
    x_data_list.append(np.linspace(0, 3, 30))
    y_data_list.append(models.expo(x_data_list[i], order, true_sigma_phi,
        true_mu, t_exposure_list[i]))
    perturbation = np.random.normal(loc=0.0, scale=0.05,
        size=x_data_list[i].shape)

    y_data_list[i] = y_data_list[i] + perturbation
    y_data_list[i] = np.clip(y_data_list[i], 0, 1)

for i in range(n_calibration):
    cal.add_calibration(t_exposure_list[i], x_data_list[i], y_data_list[i])

print("cal sigma phi:", cal.sigma_phi, cal.sigma_phi_std)
print("cal mu:", cal.mu, cal.mu_std)



fit_results = []
for i in range(n_calibration):
    fit_result = easy_fit(x_data_list[i], y_data_list[i], models.expo,
        {"order": order, "t_exposure_1": t_exposure_list[i]},
        {"sigma_phi": 5, "mu": 5}, only_positive=True)
    fit_results.append(fit_result.best_fit)

x_data_fit_list = [np.linspace(0, 3, 100)] * n_calibration
y_data_fit_list = []
y_data_true_list = []
for i, fit_result in enumerate(fit_results):
    sigma_phi = fit_result["sigma_phi"]
    mu = fit_result["mu"]
    print(i, sigma_phi, mu)
    y_data_fit_list.append(models.expo(x_data_fit_list[i], order, sigma_phi, mu,
        t_exposure_list[i]))
    y_data_true_list.append(models.expo(x_data_fit_list[i], order, true_sigma_phi, true_mu,
        t_exposure_list[i]))

for i in range(n_calibration):
    plt.plot(x_data_fit_list[i], y_data_fit_list[i])
    plt.plot(x_data_fit_list[i], y_data_true_list[i])

for i in range(n_calibration):
    plt.scatter(x_data_list[i], y_data_list[i])

plt.show()

hist = cal.bootstrap_samples["sigma_phi"]
lower = np.percentile(hist, 2.5)
upper = np.percentile(hist, 97.5)

clean_histogram = []
for value in hist:
    if lower <= value <= upper:
        clean_histogram.append(value)

plt.hist(clean_histogram, bins=30, edgecolor='black') 
plt.show()
