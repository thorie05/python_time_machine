from fitting_engine import easy_fit
from fitting_engine.models import expo
import numpy as np
import matplotlib.pyplot as plt

def perturb(y_data, scale):
    perturbation = np.random.normal(loc=0.0, scale=scale, size=y_data.shape)
    return y_data + perturbation

rng = np.random.default_rng()

scale = 0.1
order = 1.0
t_exposure = 1_000
true_mu = 5
true_sigma_phi = 5

x_data = np.linspace(0, 3, 35)
y_data = expo(x_data, order, true_sigma_phi, true_mu, t_exposure)
y_data = perturb(y_data, scale)
y_data = np.clip(y_data, 0, 1)

x_data_lst = []
y_data_lst = []
sigma_phi_lst = []
mu_lst = []

index = None
max_sigma_phi = -np.inf

for i in range(1_000):
    if i % 100 == 0:
        print(i)

    # randomly choose a new sample of data points
    random_indices = rng.choice(len(x_data), size=len(x_data), replace=True)
    x_data_resampled = x_data[random_indices]
    y_data_resampled = y_data[random_indices]

    fit_result = easy_fit(x_data_resampled, y_data_resampled, expo, {"order": order,
        "t_exposure_1": t_exposure}, {"sigma_phi": 5, "mu": 5},
        only_positive=True)

    sigma_phi = fit_result.best_fit["sigma_phi"]
    mu = fit_result.best_fit["mu"]

    sigma_phi_lst.append(sigma_phi)
    mu_lst.append(mu)
    x_data_lst.append(x_data_resampled)
    y_data_lst.append(y_data_resampled)

    if sigma_phi > max_sigma_phi:
        max_sigma_phi = sigma_phi
        index = i

print(sigma_phi_lst[index])
x_data_fit = np.linspace(0, 3, 100)
y_data_fit = expo(x_data_fit, order, sigma_phi_lst[index], mu_lst[index], t_exposure)
y_data_true = expo(x_data_fit, order, true_sigma_phi, true_mu, t_exposure)

plt.plot(x_data_fit, y_data_fit, color="red", label="fit")
plt.plot(x_data_fit, y_data_true, color="blue", label="true")
plt.scatter(x_data, y_data, color="blue", label="true")
plt.scatter(x_data_lst[index], y_data_lst[index], color="red", label="fit")
plt.legend()
plt.show()
