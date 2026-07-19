# run with PYTHONPATH=. python tests/test.py

from fitting_engine import FittingEngine
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

rng = np.random.default_rng()
engine = FittingEngine()

#########################
# True parameter values #
#########################

# true values used for generating the data
n_points = 30
true_y_err_std = 0.05

true_order = 0.0
true_sigma_phi = 5
true_mu = 5

# true values of the measured sample used for generating the data
true_t_exposure_1 = 1000

######################
# Generate test data #
######################

# generate measuremend sample data
x_data = np.linspace(0, 3, 30)
y_data = engine.models.expo(x_data, true_order, true_sigma_phi, true_mu,
    true_t_exposure_1)
# add random perturbation
perturbation = np.random.normal(loc=0.0, scale=true_y_err_std,
    size=y_data.shape)
y_data += perturbation
# allow only non-zero measurements
y_data = np.maximum(y_data, 0)

#############################
# Different Fitting Methods #
#############################

# known parameters
known_params = {"order": true_order, "sigma_phi": true_sigma_phi,
    "mu": true_mu}
# known parameter uncertainties
known_params_err_std = {"sigma_phi": 0.0, "mu": 0.0}
# bounds for unknown parameters
bounds = {"t_exposure_1": (0, 100_000)}
initial_guess = {"t_exposure_1": true_t_exposure_1}
y_err_std = np.full(x_data.shape, true_y_err_std)

####################
# Least Sqaure Fit #
####################

print("Testing Least-Squares")
lstsq_fit_result = engine.easy_fit(x_data, y_data,
    engine.models.expo, known_params, initial_guess, y_err_std=y_err_std,
    only_positive=True)

lstsq_best_fit = lstsq_fit_result.best_fit["t_exposure_1"]
lstsq_std = lstsq_fit_result.std["t_exposure_1"]
x = np.linspace(lstsq_best_fit - 3*lstsq_std, lstsq_best_fit + 3*lstsq_std,
    500)
gauss = 1/(lstsq_std*np.sqrt(2*np.pi)) \
    * np.exp(-(x-lstsq_best_fit)**2/(2*lstsq_std**2))
plt.plot(x, gauss, label="Least-Squares")

#################
# Bootstrap Fit #
#################

print("Testing Bootstrap")
bootstrap_fit_result = engine.bootstrap_fit(10_000, x_data, y_data,
    engine.models.expo, known_params, initial_guess,
    known_params_err_std=known_params_err_std, y_err_std=y_err_std,
    only_positive=True)

bootstrap_samples = np.asarray(bootstrap_fit_result.samples["t_exposure_1"])

low, high = np.percentile(bootstrap_samples, [0.5, 99.5])
bootstrap_samples = bootstrap_samples[
    (bootstrap_samples >= low) & (bootstrap_samples <= high)]

bootstrap_kde = gaussian_kde(bootstrap_samples)
x_bootstrap = np.linspace(bootstrap_samples.min(), bootstrap_samples.max(),
    500)
plt.plot(x_bootstrap, bootstrap_kde(x_bootstrap), label="Bootstrap")

#####################
# Bayesian Full Fit #
#####################

print("Testing Bayesian MCMC")
_, _, bayesian_fit_result = engine.full_fit(x_data, y_data, y_err_std,
    engine.models.expo, known_params, known_params_err_std, bounds=bounds,
    only_positive=True)

bayesian_samples = np.asarray(bayesian_fit_result.samples["t_exposure_1"])

bayesian_kde = gaussian_kde(bayesian_samples)
x_bayesian = np.linspace(bayesian_samples.min(), bayesian_samples.max(),
    500)
plt.plot(x_bayesian, bayesian_kde(x_bayesian), label="Bayesian")

#################
# Print results #
#################

print()
print("Fitting results:")
print()

print("Least-Squares Fit")
print(f"t_exposure_1: "
    f"{round(lstsq_fit_result.best_fit["t_exposure_1"], 2)}, 95% confidence: "
    f"{round(lstsq_best_fit - 2*lstsq_std, 2)} - "
    f"{round(lstsq_best_fit + 2*lstsq_std, 2)}, std: "
    f"{round(lstsq_fit_result.std["t_exposure_1"], 2)}")

print("Bootstrap Fit")
print(f"t_exposure_1: "
    f"{round(bootstrap_fit_result.best_fit["t_exposure_1"], 2)}, "
    f"95% confidence: {round( \
    bootstrap_fit_result.confidence_interval["t_exposure_1"][0], 2)} - "
    f"{round(\
    bootstrap_fit_result.confidence_interval["t_exposure_1"][1], 2)}")

print("Bayesian Fit")
print(f"t_exposure_1: "
    f"{round(bayesian_fit_result.best_fit["t_exposure_1"], 2)}, "
    f"95% confidence: {round( \
    bayesian_fit_result.confidence_interval["t_exposure_1"][0], 2)} - "
    f"{round(\
    bayesian_fit_result.confidence_interval["t_exposure_1"][1], 2)}")

plt.legend()
plt.show()
