from fitting_engine import easy_fit
from fitting_engine import bootstrap_fit
from fitting_engine.models import expo
import numpy as np
import matplotlib.pyplot as plt

def perturb(y_data, scale):
    perturbation = np.random.normal(loc=0.0, scale=scale, size=y_data.shape)
    return y_data + perturbation

order = 1.0
mu = 5
sigma_phi = 5

true_t_exposure = 1000

x_data = np.linspace(0, 3, 30)

y_data = expo(x_data, order, sigma_phi, mu, true_t_exposure)

real_fits = []
for i in range(10_000):
    if i % 100 == 0:
        print(i)
    y_data_perturbed = perturb(y_data, 0.1)
    y_data_perturbed = np.clip(y_data_perturbed, 0, 1)

    fit_result = easy_fit(x_data, y_data_perturbed, expo, {"order": order,
        "sigma_phi": sigma_phi, "mu": mu}, {"t_exposure_1": 1_000},
        only_positive=True)

    fitted_t_exposure = fit_result.best_fit["t_exposure_1"]
    real_fits.append(fitted_t_exposure)

y_data = perturb(y_data, 0.1)
bootstrap_fit_result = bootstrap_fit(10_000, x_data, y_data, expo,
    {"order": order, "sigma_phi": sigma_phi, "mu": mu}, {"t_exposure_1": 1_000},
    only_positive=True, return_samples=True)
bootstrap_hist = bootstrap_fit_result.bootstrap_samples["t_exposure_1"]
lower = np.percentile(bootstrap_hist, 0.1)
upper = np.percentile(bootstrap_hist, 99.9)

clean_histogram = []
for value in bootstrap_hist:
    if lower <= value <= upper:
        clean_histogram.append(value)

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)
ax1.hist(real_fits, bins=30, edgecolor="black")
ax1.set_title("Real guesses")

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
ax2.hist(clean_histogram, bins=30, edgecolor="black")
ax2.set_title("Bootstrap guesses")

plt.show(block=False)
plt.pause(0.1)
plt.show()
