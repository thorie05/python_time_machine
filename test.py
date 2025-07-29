from fitting_engine import get_initial_guess
from fitting_engine import bootstrap_fit
from fitting_engine import bayesian_fit
import numpy as np
import matplotlib.pyplot as plt
from fitting_engine import models

order = 0.0
sigma_phi = 5
mu = 5
f = 0.0001
t_exposure_1 = 3_000
t_burial_1 = 10_000
t_exposure_2 = 100

x_data = np.linspace(0, 3, 30)
y_data = models.expo_buri_expo(x_data, order, sigma_phi, mu, f, t_exposure_1,
    t_burial_1, t_exposure_2)

perturbation = np.random.normal(loc=0.0, scale=0.05, size=x_data.shape)
y_data = y_data + perturbation
y_data = np.maximum(0, y_data)
y_err_std = np.full(fill_value=0.05, shape=30)

known_params = {"order": order, "sigma_phi": sigma_phi, "mu": mu, "f": f}
known_params_err_std = {"order": 0.0, "sigma_phi": 0.0, "mu": 0.0, "f": 0.00001}
bounds = {"t_exposure_1": (0, 1_000_000), "t_burial_1": (0, 1_000_000),
    "t_exposure_2": (0, 1_000_000)}

initial_guess = get_initial_guess(x_data, y_data, models.expo_buri_expo,
    known_params, bounds=bounds, y_err_std=y_err_std)

print(initial_guess)

bootstrap_fit_result = bootstrap_fit(2_000, x_data, y_data,
    models.expo_buri_expo, known_params, initial_guess, y_err_std=y_err_std,
    known_params_err_std=known_params_err_std, only_positive=True)

free_params_priors = {}
for param_name, param_best_fit in bootstrap_fit_result.best_fit.items():
    lower, upper = bootstrap_fit_result.confidence_interval [param_name]
    prior_std = max(param_best_fit - lower, upper - param_best_fit)
    free_params_priors[param_name] = (param_best_fit, prior_std)

    print(param_name, lower, upper)

bayesian_fit_result = bayesian_fit(4_000, 2_000, x_data, y_data,
    models.expo_buri_expo, known_params, free_params_priors, y_err_std,
    known_params_err_std=known_params_err_std, only_positive=True,
    target_accept=0.95)

if not bayesian_fit_result.success:
    print("Problems occured: The fit results may not be reliable.")

# t_exposure_1
t_exposure_1_fit = bayesian_fit_result.best_fit["t_exposure_1"]
t_exposure_1_confidence_interval \
    = bayesian_fit_result.confidence_interval["t_exposure_1"]

# t_burial_1
t_burial_1_fit = bayesian_fit_result.best_fit["t_burial_1"]
t_burial_1_confidence_interval \
    = bayesian_fit_result.confidence_interval["t_burial_1"]

# t_exposure_2
t_exposure_2_fit = bayesian_fit_result.best_fit["t_exposure_2"]
t_exposure_2_confidence_interval \
    = bayesian_fit_result.confidence_interval["t_exposure_2"]

# calculate fit graphs
y_fit = models.expo_buri_expo(x_data, order, sigma_phi, mu, f, t_exposure_1_fit,
    t_burial_1, t_exposure_2)

print("t_exposure_1:", t_exposure_1_fit)
print("95% confidence interval:", *t_exposure_1_confidence_interval)
print()
print("t_burial_1:", t_burial_1_fit)
print("95% confidence interval:", *t_burial_1_confidence_interval)
print()
print("t_exposure_2:", t_exposure_2_fit)
print("95% confidence interval:", *t_exposure_2_confidence_interval)

print()
print("time since exposure 1:", bayesian_fit_result.time_since_events[0])
print("time since burial 1:", bayesian_fit_result.time_since_events[1])
print("time since exposure 2:", bayesian_fit_result.time_since_events[2])

plt.scatter(x_data, y_data)
plt.plot(x_data, y_fit)
plt.show()
