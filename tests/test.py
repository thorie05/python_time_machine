# run with PYTHONPATH=. python tests/test.py

from fitting_engine import FittingEngine
import numpy as np
import matplotlib.pyplot as plt

def main():
    engine = FittingEngine(verbose=True)

    #########################
    # True parameter values #
    #########################

    # true values used for generating the data
    n_points = 30
    true_y_err_std = 0.05
    x_length = 3

    true_order = 0.0
    true_order_std = 0.0
    true_sigma_phi = 5
    true_mu = 5
    true_f = 0.0001
    f_std = 0.00001

    # true values of the measured sample used for generating the data
    true_t_exposure_1 = 3_000
    true_t_burial_1 = 5_000
    true_t_exposure_2 = 10
    true_t_burial_2 = 3_000

    # exposure times of the calibration samples
    calibration_t_exposure = [10]


    ######################
    # Generate test data #
    ######################

    # generate calibration data with random perturbation from true values
    calibration_x_data = []
    calibration_y_data = []
    calibration_y_err_std = []
    for i, t_exposure in enumerate(calibration_t_exposure):
        calibration_x_data.append(np.linspace(0, x_length, n_points))
        # genearte y data using the mathematical model for single exposure
        calibration_y_data.append(engine.models.expo(calibration_x_data[i],
            true_order, true_sigma_phi, true_mu, t_exposure))
        # add random perturbation
        perturbation = np.random.normal(loc=0.0, scale=true_y_err_std,
            size=calibration_x_data[i].shape)

        calibration_y_data[i] += perturbation
        # allow only non-zero measurements
        calibration_y_data[i] = np.maximum(calibration_y_data[i], 0)

        calibration_y_err_std.append(np.full(len(calibration_x_data[0]),
            true_y_err_std))

    # generate measuremend sample data
    x_data = np.linspace(0, x_length, n_points)
    y_data = engine.models.expo_buri_expo_buri(x_data, true_order, true_sigma_phi,
        true_mu,true_f, true_t_exposure_1, true_t_burial_1, true_t_exposure_2,
        true_t_burial_2)
    # add random perturbation
    perturbation = np.random.normal(loc=0.0, scale=true_y_err_std,
        size=calibration_x_data[i].shape)
    y_data += perturbation
    # allow only non-zero measurements
    y_data = np.maximum(y_data, 0)

    # generate known f by perturbing the true value according to std
    known_f = np.random.normal(loc=true_f, scale=f_std)


    #############
    # Calibrate #
    #############

    # combine individual calibration samples into one large dataset
    calibration_x_data_combined = np.concatenate(calibration_x_data)
    calibration_y_data_combined = np.concatenate(calibration_y_data)
    calibration_y_err_std_combined = np.concatenate(calibration_y_err_std)

    # each datapoint gets an individual t_exposure value for the global fit
    calibration_t_exposure_combined = np.concatenate(
        [np.full(n_points, t_exposure) for t_exposure in calibration_t_exposure])

    # order is a scalar that is constant for all datapoints, t_exposure_1 
    # can differ between datapoints because multiple calibration datasets
    # can be used
    known_params = {"order": true_order,
        "t_exposure_1": calibration_t_exposure_combined}
    known_params_err_std = {"order": true_order_std}
    bounds = {
        "sigma_phi": engine.param_bounds.val.sigma_phi,
        "mu": engine.param_bounds.val.mu
    }

    # calculate calibration results
    _, _, calibration_fit_result = engine.full_fit(calibration_x_data_combined,
        calibration_y_data_combined, calibration_y_err_std_combined,
        engine.models.expo, known_params, known_params_err_std, bounds=bounds,
        fit_quality=engine.fit_quality_settings.medium, only_positive=True)

    joint_samples = calibration_fit_result.joint_samples

    # plot 2d histogram
    sigma_phi_joint = np.array(
        [sample["sigma_phi"] for sample in joint_samples])
    mu_joint = np.array([sample["mu"] for sample in joint_samples])
    hist, x_edges, y_edges = np.histogram2d(sigma_phi_joint, mu_joint,
        bins=50, density=True)
    plt.figure(figsize=(10, 10))
    plt.imshow(hist.T, origin="lower", aspect="auto",
        extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]],
        cmap="viridis")
    plt.colorbar(label="Probability density")
    plt.xlabel("sigma_phi")
    plt.ylabel("mu")
    plt.title("Joint probability distribution")
    plt.tight_layout()
    plt.savefig(f"calibration_2d_distribution_{"_".join(
        [str(t) for t in calibration_t_exposure])}.png", dpi=300,
        bbox_inches="tight")
    plt.show()

    exit()

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
        "t_exposure_2": (0, 100_000), "t_burial_2": (0, 100_000)}
    y_err_std = np.full(x_data.shape, true_y_err_std)

    print("Starting fit with:")
    print(f"order: {true_order}")
    print(f"sigma_phi: {cal.sigma_phi}, std: {cal.sigma_phi_std}")
    print(f"mu: {cal.mu}, std: {cal.mu_std}")
    print(f"f: {known_f}, std: {f_std}")
    print()

    fit_result = full_fit(x_data, y_data, y_err_std, models.expo_buri_expo_buri,
        known_params, known_params_err_std, bounds=bounds, only_positive=True)


    #################
    # Print results #
    #################

    if not fit_result.success:
        print("Problems occured: The fit results may not be reliable.")
        print()

    print("Fitting results:")
    print()

    t_exposure_1 = fit_result.best_fit["t_exposure_1"]
    t_burial_1 = fit_result.best_fit["t_burial_1"]
    t_exposure_2 = fit_result.best_fit["t_exposure_2"]
    t_burial_2 = fit_result.best_fit["t_burial_2"]

    print("Timespans:")
    print(f"t_exposure_1: {t_exposure_1}, 95% confidence: "
        f"{fit_result.confidence_interval["t_exposure_1"][0]} - "
        f"{fit_result.confidence_interval["t_exposure_1"][1]}")
    print(f"t_burial_1: {t_burial_1}, 95% confidence: "
        f"{fit_result.confidence_interval["t_burial_1"][0]} - "
        f"{fit_result.confidence_interval["t_burial_1"][1]}")
    print(f"t_exposure_2: {t_exposure_2}, 95% confidence: "
        f"{fit_result.confidence_interval["t_exposure_2"][0]} - "
        f"{fit_result.confidence_interval["t_exposure_2"][1]}")
    print(f"t_burial_2: {t_burial_2}, 95% confidence: "
        f"{fit_result.confidence_interval["t_burial_2"][0]} - "
        f"{fit_result.confidence_interval["t_burial_2"][1]}")
    print()

    time_since_exposure_1 = fit_result.time_since_events[0]
    time_since_burial_1 = fit_result.time_since_events[1]
    time_since_exposure_2 = fit_result.time_since_events[2]
    time_since_burial_2 = fit_result.time_since_events[3]

    print("Time since events:")
    print(f"time since exposure 1: {time_since_exposure_1[0]}, 95% confidence: "
        f"{time_since_exposure_1[1][0]} - {time_since_exposure_1[1][1]}")
    print(f"time since burial 1: {time_since_burial_1[0]}, 95% confidence: "
        f"{time_since_burial_1[1][0]} - {time_since_burial_1[1][1]}")
    print(f"time since exposure 2: {time_since_exposure_2[0]}, 95% confidence: "
        f"{time_since_exposure_2[1][0]} - {time_since_exposure_2[1][1]}")
    print(f"time since burial 2: {time_since_burial_2[0]}, 95% confidence: "
        f"{time_since_burial_2[1][0]} - {time_since_burial_2[1][1]}")


    #####################
    # Plot fitted curve #
    #####################

    # calculate fitted curve
    x_data_fit = np.linspace(0, 3, 500)
    y_data_fit = models.expo_buri_expo_buri(x_data_fit, true_order, cal.sigma_phi,
        cal.mu, known_f, t_exposure_1, t_burial_1, t_exposure_2, t_burial_2)

    plt.scatter(x_data, y_data, color="red")
    plt.plot(x_data_fit, y_data_fit)
    plt.ylim(bottom=0)
    plt.show()

if __name__ == "__main__":
    main()
