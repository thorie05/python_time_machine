from easy_fit import easy_fit
from bootstrap_fit import bootstrap_fit
import numpy as np
import matplotlib.pyplot as plt
import models

order = 1.0
sigma_phi = 5
mu = 5
f = 0.1
t_expo_1 = 300

x_data = np.linspace(0, 3, 30)
y_data = models.expo(x_data, order, sigma_phi, mu, t_expo_1)

perturbation = np.random.normal(loc=0.0, scale=0.05, size=x_data.shape)
y_data = y_data + perturbation
y_data = np.clip(y_data, 0, 1)

easy_fit_result = easy_fit(x_data, y_data, models.expo, {"order": order,
    "sigma_phi": sigma_phi, "mu": mu}, {"t_expo_1": 300})

bootstrap_fit_result, bootstrap_fit_result_lists = bootstrap_fit(10000, x_data,
    y_data, models.expo, {"order": order, "sigma_phi": sigma_phi, "mu": mu},
    {"t_expo_1": 300}, known_params_err_sigma={"order": 0.0, "sigma_phi": 0.5,
    "mu": 0.5})

t_expo_1_easy_fit = easy_fit_result["t_expo_1"]
t_expo_1_bootstrap_fit = bootstrap_fit_result["t_expo_1"][0]
t_expo_1_confidence_interval = bootstrap_fit_result["t_expo_1"][1]

y_easy_fit = models.expo(x_data, order, sigma_phi, mu, t_expo_1_easy_fit)
y_bootstrap_fit = models.expo(x_data, order, sigma_phi, mu,
    t_expo_1_bootstrap_fit)

print("t_exp_1, according to easy fit:", t_expo_1_easy_fit)
print("t_exp_1, according to bootstrap fit:", t_expo_1_bootstrap_fit)
print("95% confidence interval:", *t_expo_1_confidence_interval)

bootstrap_fit_histogram = bootstrap_fit_result_lists["t_expo_1"]
clean_histogram = []
for value in bootstrap_fit_histogram:
    if t_expo_1_confidence_interval[0] <= value \
        <= t_expo_1_confidence_interval[1]:
        clean_histogram.append(value)

plt.scatter(x_data, y_data)
plt.plot(x_data, y_easy_fit)
plt.plot(x_data, y_bootstrap_fit)
plt.show()

plt.hist(clean_histogram, bins=50, edgecolor='black') 
plt.show()
