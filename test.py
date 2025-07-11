from easy_fit import easy_fit
from bootstrap_fit import bootstrap_fit
import numpy as np
import matplotlib.pyplot as plt
import models

order = 1.0
sigma_phi = 5
mu = 5
f = 0.0001
t_exposure_1 = 3000
t_burial_1 = 10000
t_exposure_2 = 10

x_data = np.linspace(0, 3, 30)
y_data = models.expo_buri_expo(x_data, order, sigma_phi, mu, f, t_exposure_1,
    t_burial_1, t_exposure_2)

perturbation = np.random.normal(loc=0.0, scale=0.05, size=x_data.shape)
y_data = y_data + perturbation
y_data = np.clip(y_data, 0, 1)

easy_fit_result = easy_fit(x_data, y_data, models.expo_buri_expo,
    {"order": order, "sigma_phi": sigma_phi, "mu": mu, "f": f},
    {"t_exposure_1": 1000, "t_burial_1": 100, "t_exposure_2": 100},
    only_positive=True)

bootstrap_fit_result = bootstrap_fit(10_000, x_data,
    y_data, models.expo_buri_expo, {"order": order, "sigma_phi": sigma_phi,
    "mu": mu, "f": f}, {"t_exposure_1": 300, "t_burial_1": 100,
    "t_exposure_2": 100}, known_params_err_sigma={"order": 0.0, "sigma_phi":
    0.0, "mu": 0.0, "f": 0.0}, only_positive=True, return_samples=True)

# t_exposure_1 fit
t_exposure_1_easy_fit = easy_fit_result.best_fit["t_exposure_1"]
t_exposure_1_bootstrap_fit = bootstrap_fit_result.best_fit["t_exposure_1"]

# t_exposure_1 confidence interval
t_exposure_1_confidence_interval = \
    bootstrap_fit_result.confidence_interval["t_exposure_1"]

# t_burial_1 fit
t_burial_1_easy_fit = easy_fit_result.best_fit["t_burial_1"]
t_burial_1_bootstrap_fit = bootstrap_fit_result.best_fit["t_burial_1"]

# t_burial_1 confidence iterval
t_burial_1_confidence_interval = \
    bootstrap_fit_result.confidence_interval["t_burial_1"]

# t_exposure_2 fit
t_exposure_2_easy_fit = easy_fit_result.best_fit["t_exposure_2"]
t_exposure_2_bootstrap_fit = bootstrap_fit_result.best_fit["t_exposure_2"]

# t_exposure_2_confidence_interval
t_exposure_2_confidence_interval = \
    bootstrap_fit_result.confidence_interval["t_exposure_2"]

# calculate fit graphs easy fit
y_easy_fit = models.expo_buri_expo(x_data, order, sigma_phi, mu, f,
    t_exposure_1_easy_fit, t_burial_1_easy_fit, t_exposure_2_easy_fit)

# calculate fit graphs bootstrap fit
y_bootstrap_fit = models.expo_buri_expo(x_data, order, sigma_phi, mu, f,
    t_exposure_1_bootstrap_fit, t_burial_1_bootstrap_fit,
    t_exposure_2_bootstrap_fit)

print("t_exposure_1, according to easy fit:", t_exposure_1_easy_fit)
print("t_exposure_1, according to bootstrap fit:", t_exposure_1_bootstrap_fit)
print("95% confidence interval:", *t_exposure_1_confidence_interval)

print()

print("t_burial_1, according to easy fit:", t_burial_1_easy_fit)
print("t_burial_1, according to bootstrap fit:", t_burial_1_bootstrap_fit)
print("95% confidence interval:", *t_burial_1_confidence_interval)

print()

print("t_exposure_2, according to easy fit:", t_exposure_2_easy_fit)
print("t_exposure_2, according to bootstrap fit:", t_exposure_2_bootstrap_fit)
print("95% confidence interval:", *t_exposure_2_confidence_interval)

bootstrap_fit_histogram = bootstrap_fit_result.bootstrap_samples["t_exposure_1"]
clean_histogram = []
for value in bootstrap_fit_histogram:
    if t_exposure_1_confidence_interval[0] <= value \
        <= t_exposure_1_confidence_interval[1]:
        clean_histogram.append(value)

plt.scatter(x_data, y_data)
plt.plot(x_data, y_easy_fit)
plt.plot(x_data, y_bootstrap_fit)
plt.show()

plt.hist(clean_histogram, bins=30, edgecolor='black') 
plt.show()
