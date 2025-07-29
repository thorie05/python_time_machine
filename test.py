from fitting_engine import Calibrator, models, full_fit
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng()

#########################
# True parameter values #
#########################

# true values used for generating the data
n_points = 30
true_y_err_std = 0.05

true_order = 0.0
true_sigma_phi = 5
true_mu = 5
true_f = 0.0001
f_std = 0.00001

# true values of the measured sample used for generating the data
true_t_exposure_1 = 3_000
true_t_burial_1 = 10_000
true_t_exposure_2 = 100

# exposure times of the calibration samples
calibration_t_exposure = [10, 100, 1000] 


######################
# Generate test data #
######################

# generate calibration data with random perturbation from true values
calibration_x_data = []
calibration_y_data = []
calibration_y_err_std = []
for i, t_exposure in enumerate(calibration_t_exposure):
    calibration_x_data.append(np.linspace(0, 3, n_points))
    # genearte y data using the mathematical model for single exposure
    calibration_y_data.append(models.expo(calibration_x_data[i], true_order,
        true_sigma_phi, true_mu, t_exposure))
    # add random perturbation
    perturbation = np.random.normal(loc=0.0, scale=true_y_err_std,
        size=calibration_x_data[i].shape)

    calibration_y_data[i] = calibration_y_data[i] + perturbation
    # allow only non-zero measurements
    calibration_y_data[i] = np.maximum(calibration_y_data[i], 0)

    calibration_y_err_std.append(np.full(len(calibration_x_data[0]),
        true_y_err_std))

# generate measuremend sample data
x_data = np.linspace(0, 3, 30)
y_data = models.expo_buri_expo(x_data, true_order, true_sigma_phi, true_mu,
    true_f, true_t_exposure_1, true_t_burial_1, true_t_exposure_2)

# generate known f by perturbing the true value according to std
known_f = np.random.normal(loc=true_f, scale=f_std)


#############
# Calibrate #
#############

# set up calibrator object
cal = Calibrator(true_order, 0.0)

# add calibration samples to calibrator
for i, t_exposure in enumerate(calibration_t_exposure):
    cal.add_calibration(t_exposure, calibration_x_data[i],
        calibration_y_data[i], calibration_y_err_std[i])

print("Calibration results:")
print(f"sigma_phi: {cal.sigma_phi}, std: {cal.sigma_phi_std}")
print(f"mu: {cal.mu}, std: {cal.mu_std}")
print()


######################
# Actual measurement #
######################

# known parameters
known_params = {"order": true_order, "sigma_phi": cal.sigma_phi, "mu": cal.mu,
    "f": known_f}
# known parameter uncertainties
known_params_err_std = {"sigma_phi": cal.sigma_phi_std, "mu": cal.mu_std,
    "f": f_std}
# bounds for unknown parameters
bounds = {"t_exposure_1": (0, 100_000), "t_burial_1": (0, 100_000),
    "t_exposure_2": (0, 100_000)}
y_err_std = np.full(x_data.shape, true_y_err_std)

print("Starting fit with:")
print(f"order: {true_order}")
print(f"sigma_phi: {cal.sigma_phi}, std: {cal.sigma_phi_std}")
print(f"mu: {cal.mu}, std: {cal.mu_std}")
print(f"f: {known_f}, std: {f_std}")
print()

fit_result = full_fit(x_data, y_data, y_err_std, models.expo_buri_expo,
    known_params, known_params_err_std, bounds=bounds, only_positive=True)


###################
# Fitting results #
###################

if not fit_result.success:
    print("Problems occured: The fit results may not be reliable.")
    print()

time_since_exposure_1 = fit_result.time_since_events[0]
time_since_burial_1 = fit_result.time_since_events[1]
time_since_exposure_2 = fit_result.time_since_events[2]

print("Fitting results:")

print("Timespans:")
print(f"t_exposure_1: {fit_result.best_fit["t_exposure_1"]}, 95% confidence: "
    f"{fit_result.confidence_interval["t_exposure_1"][0]} - "
    f"{fit_result.confidence_interval["t_exposure_1"][1]}")
print(f"t_burial_1: {fit_result.best_fit["t_burial_1"]}, 95% confidence: "
    f"{fit_result.confidence_interval["t_burial_1"][0]} - "
    f"{fit_result.confidence_interval["t_burial_1"][1]}")
print(f"t_exposure_2: {fit_result.best_fit["t_exposure_2"]}, 95% confidence: "
    f"{fit_result.confidence_interval["t_exposure_2"][0]} - "
    f"{fit_result.confidence_interval["t_exposure_2"][1]}")

print("Time since events:")
print(f"time since exposure 1: {time_since_exposure_1[0]}, 95% confidence: "
    f"{time_since_exposure_1[1][0]} - {time_since_exposure_1[1][1]}")
print(f"time since burial 1: {time_since_burial_1[0]}, 95% confidence: "
    f"{time_since_burial_1[1][0]} - {time_since_burial_1[1][1]}")
print(f"time since exposure 2: {time_since_exposure_2[0]}, 95% confidence: "
    f"{time_since_exposure_2[1][0]} - {time_since_exposure_2[1][1]}")
