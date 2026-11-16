import numpy as np
import emcee
from .fit_result import FitResult


def bayesian_fit(draws, tune, x_data, y_data, y_err_std,
    model_function, initial_guess, free_params_bounds,
    known_params_distribution, n_walkers=None, seed=None,
    verbose=False, only_positive=False):
    """
    A function that takes datapoints and a mathematical model function to
    calculate the best fit of the model through the datapoints as well as the
    uncertainties for all fitting parameters. Uses the Bayesian MCMC method from
    the emcee module. Free parameters are sampled according to a uniform prior
    within their specified bounds. Known parameters can be treated as fixed,
    normally distributed or distributed according to custom log-probability
    density functions. This also allows for joint probability
    distributions of multiple correlated parameters. Assumes independent
    normally distributed uncertainties of the measured y-values. Only the
    free parameters are included in the returned fitting results and samples.

    Args:
        draws (int): Number of MCMC sampling steps per walker.
        tune (int): Number of burn-in steps per walker.
        x_data (numpy.ndarray): The x-values of the data points.
        y_data (numpy.ndarray): The y-values of the data points.
        y_err_std (numpy.ndarray): The standard deviation of the y-values.
        model_function (callable): The model function to be used for fitting.
        initial_guess (dict(str: float)): A dict mapping the names of all
            sampled parameters (free parameters and uncertain known parameters)
            to their initial values. The walkers are initialized with small
            random perturbations around these values.
        free_params_bounds (dict(str: Tuple(float, float))): A dict mapping
            the free parameter names to tuples containing their lower and upper
            bounds. Serves as a uniform prior for the MCMC model.
        known_params_distribution (dict(tuple(str): tuple or callable)):
            A dict mapping tuples of known parameter names to their respective
            probability distributions. For individual parameters a tuple
            containing the mean value and standard deviation of a normal
            distribution can be passed. If the standard deviation is 0 the
            parameter is treated as fixed. In this case the value can also be
            a numpy array containing individual parameter values for each data
            point. Alternatively, a callable returning the log-probability
            density can be passed for individual or multiple jointly
            distributed parameters. The callable takes the parameter values
            as positional arguments in the order specified by the tuple of
            parameter names and returns a scalar log-probability density.
        n_walkers (int, optional): Number of MCMC walkers. If not specified,
            the maximum of 32 and twice the number of sampled parameters is
            used.
        seed (int, optional): Optional random number generator seed.
        verbose (bool, optional): Optional flag controlling console output.
        only_positive (bool, optional): Flag that controls if the sampled
            parameters are allowed to be only non-negative.

    Returns:
        FitResult: Dataclass containing all relevant information about a fit.
            See documentation for details.
    """

    # separate fixed parameters and prior distributions
    fixed_params = {}
    normal_priors = {}
    custom_priors = {}

    for param_names, distribution in known_params_distribution.items():
        if callable(distribution):
            custom_priors[param_names] = distribution
        else:
            param_name = param_names[0]
            mu, std = distribution

            if std == 0:
                fixed_params[param_name] = mu
            else:
                normal_priors[param_name] = (mu, std)

    # determine sampled parameters and their initial values
    sampled_param_names = list(initial_guess.keys())
    ndim = len(sampled_param_names)
    theta_init = np.array(list(initial_guess.values()), dtype=float)

    # convert parameter vector to parameter dictionary
    def unpack_params(theta):
        return dict(zip(sampled_param_names, theta))

    def log_prior(theta):
        if only_positive and np.any(theta < 0):
            return -np.inf

        params = unpack_params(theta)
        lp = 0.0

        # uniform priors for free parameters
        for param_name, (lower, upper) in free_params_bounds.items():
            if not lower <= params[param_name] <= upper:
                return -np.inf

        # normal priors for uncertain known parameters
        for param_name, (mu, std) in normal_priors.items():
            lp -= 0.5 * ((params[param_name] - mu) / std)**2

        # custom priors for individual or correlated parameters
        for param_names, logpdf in custom_priors.items():
            lp += logpdf(*(params[name] for name in param_names))

        return lp

    def log_likelihood(theta):
        params = unpack_params(theta)
        model_y = model_function(x_data, **fixed_params, **params)

        return -0.5 * np.sum(((y_data - model_y) / y_err_std)**2)

    def log_posterior(theta):
        lp = log_prior(theta)

        if not np.isfinite(lp):
            return -np.inf

        ll = log_likelihood(theta)

        if not np.isfinite(ll):
            return -np.inf

        return lp + ll

    rng = np.random.default_rng(seed)

    if n_walkers is None:
        n_walkers = max(32, 8 * ndim)

    scale = 1e-2 * np.where(theta_init != 0, np.abs(theta_init), 1.0)

    initial_positions = np.empty((n_walkers, ndim))

    for i in range(n_walkers):
        while True:
            position = theta_init + rng.normal(size=ndim) * scale

            if np.isfinite(log_posterior(position)):
                initial_positions[i] = position
                break

    sampler = emcee.EnsembleSampler(n_walkers, ndim, log_posterior,
    moves=[(emcee.moves.DEMove(), 0.8),
        (emcee.moves.DESnookerMove(), 0.2)])

    if seed is not None:
        sampler.random_state = np.random.RandomState(seed).get_state()

    # burn-in phase
    state = sampler.run_mcmc(initial_positions, tune, progress=verbose)
    sampler.reset()

    # production phase
    sampler.run_mcmc(state, draws, progress=verbose)

    # extract samples
    samples = sampler.get_chain(flat=True)

    best_fit = {}
    confidence_interval = {}
    std = {}
    marginal_samples = {}
    joint_samples = []

    for param_name in free_params_bounds:
        idx = sampled_param_names.index(param_name)
        param_samples = samples[:, idx]

        lower, upper = np.percentile(param_samples, [15.865, 84.135])

        best_fit[param_name] = float(np.median(param_samples))
        confidence_interval[param_name] = (float(lower), float(upper))

        # median absolute deviation as robust std estimate
        std[param_name] = 1.4826 * np.median(
            np.abs(param_samples - best_fit[param_name]))

        marginal_samples[param_name] = param_samples

    for sample in samples:
        params = unpack_params(sample)
        joint_samples.append({
            name: float(params[name]) for name in free_params_bounds
        })

    # calculate rmse using posterior medians of all sampled parameters
    median_params = unpack_params(np.median(samples, axis=0))
    y_data_fit = model_function(x_data, **fixed_params, **median_params)
    rmse = np.sqrt(np.mean((y_data_fit - y_data)**2))

    # check convergence using integrated autocorrelation time
    tau = sampler.get_autocorr_time(tol=0)
    ess = draws * n_walkers / tau

    tau_ok = np.all(draws > 50 * tau)
    ess_ok = np.all(ess > 1000)

    success = bool(tau_ok and ess_ok)

    # extract effective sample sizes of free parameters
    ess_dict = {name: float(ess[sampled_param_names.index(name)])
        for name in free_params_bounds}

    result = FitResult(success=success, best_fit=best_fit,
        confidence_interval=confidence_interval, std=std, rmse=rmse,
        marginal_samples=marginal_samples, joint_samples=joint_samples,
        ess=ess_dict)

    return result
