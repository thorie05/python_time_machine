from fitting_engine import easy_fit
from fitting_engine.models import expo
import numpy as np
import matplotlib.pyplot as plt

def perturb(y_data, scale):
    perturbation = np.random.normal(loc=0.0, scale=scale, size=y_data.shape)
    return y_data + perturbation

order = 1.0
mu = 5
sigma_phi = 5
true_t_exposure = 1_000
scale = 0.1

def scientist_experiment(n):
    # generate osl data
    x_data = np.linspace(0, 3, n)
    y_data = expo(x_data, order, sigma_phi, mu, true_t_exposure)
    y_data = perturb(y_data, scale)
    y_data = np.clip(y_data)

    # find t_exposure
    fit_result = easy_fit(x_data, y_data, expo,
        {"order": order, "sigma_phi": sigma_phi, "mu": mu},
        {"t_exposure_1": 1_000}, only_positive=True)

    t_exposure = fit_result.best_fit["t_exposure_1"]
    return t_exposure

results = {}

for n in range(10, 200):
    print(n)
    results[n] = []
    for _ in range(10_000):
        t_exposure = scientist_experiment(n)
        results[n].append(t_exposure)

stds = []
for n in results.keys():
    std = float((np.percentile(results[n], 84.13) \
        - np.percentile(results[n], 15.87))) / 2
    stds.append(std / true_t_exposure)

plt.scatter(results.keys(), stds)
plt.xlabel('Number of Data Points (N)')
plt.ylabel('Relative Standard Deviation of Exposure Time Estimate')
plt.show()
