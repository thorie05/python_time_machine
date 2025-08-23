**Python Time Machine**

The Python Time Machine consists of two parts: A fitting engine and the
graphical user interface. The fitting engine is located in the
`fitting_engine` folder, the user interface in the `gui` folder. To start the
GUI, run `main.py` (optional `--verbose` flag for console output).

**Fitting Engine**

The `fitcore` folder hosts functionality that is not OSL-specific but could
be used for all fitting purposes. Files directly in the `fitting_engine` folder
are OSL-specific, like `models.py` which implements the mathematical model
functions. The fitting engine exposes different methods that can be used for a
fit.

* `easy_fit`:  
  A normal SciPy least-squares fit that finds the maximum likelihood values
  for the fit parameters given a model function and input data. The standard
  error estimates are omitted as they are not accurate for highly non-linear
  functions, like the luminescence model functions. `easy_fit` always
  requires an initial guess, because it can only find the nearest local
  minimum.

* `get_initial_guess`:  
  Uses SciPy's `differential_evolution` to find the global minimum, which
  can serve as an initial guess for `easy_fit`. In theory, it is not
  guaranteed that the algorithm always finds the global minimum. Therefore, the
  parameter bounds are very important for the initial guess finder because
  they constrain the search space. In practice however, the method should almost
  always find the global minimum, especially with high fit quality settings.

* `bootstrap_fit`:  
  Runs `easy_fit` many times while resampling input data to obtain a probability
  distribution of the best fit parameters and thus estimating the
  uncertainties. It can also handle uncertain known parameters, by
  additionally perturbing them according to the given standard deviation.
  The bootstrap results can become unstable when there are only a few data
  points that heavily influence the fit result, which is the case for a
  bleaching front curve. Therefore, the bootstrap fit should only serve as
  a rough estimator.

* `bayesian_fit`:  
  Uses MCMC (Markov chain Monte Carlo) from the PyMC module to produce any
  number of random samples from the parameter space that follow the true
  probability distribution. Thus, with a large enough number of samples one
  can obtain the probability distribution (posterior) for each parameter and
  calculate confidence intervals. However, in order to work efficiently, MCMC
  needs prior knowledge about each parameter to constrain the parameter
  space.

* `full_fit`:  
  The `full_fit` function first finds an initial guess with
  `get_initial_guess` which is needed for `bootstrap_fit`. Then it uses
  `bootstrap_fit` to estimate the uncertainties of the fit parameters and
  uses the results as priors for `bayesian_fit`. It is very important that
  the priors are not too tight, since this would bias the result. Therefore,
  the standard deviation for every fit parameter of the bootstrap result is
  doubled to always ensure conservative guesses, but still constrain the MCMC
  search space. Since the bootstrap fit results can sometimes blow up, the
  relative standard deviation is capped at 1 to prevent unreasonably wide
  priors. These values are not necessarily perfect and could benefit from
  further tweaking. If the priors are too conservative, the MCMC fit could take
  longer, but the results should always be correct. If the priors are too tight,
  then the results become wrong, so good prior estimation is very important.

* `get_event_ages`:  
  To obtain the age of an event it's not accurate to simply add all
  timespans of the following events, especially not for the confidence
  intervals. `get_event_ages` calculates the true event ages based on the
  posterior samples obtained from `bayesian_fit`.

To view the posterior distribution of a fit, one can double-click a result in
the result table, which opens a histogram window. The distribution should look
plausible, but doesn't have resemble a normal distribution. To further confirm
that a fit result is reliable, it is also helpful to export the xlsx results of
the MCMC fit and view the fit details. First, one can verify that
`get_initial_guess` has found a global minimum. The initial should be close to
the best fit results, the graph of which should visually resemble the input
data. Furthermore, `free_params_priors` contains the mu (mean) and sigma
(standard deviation) values of the fit parameters that are used as priors for
the MCMC fit. Mu should again be close to the best fit values, sigma should be
approximately two times larger than the standard deviation of the MCMC result.
If it's not significantly larger, then the priors were too restrictive and the
result is not reliable.

For a normal fit, the known fitting parameters are the material properties of
the rock (`order`, `sigma_phi`, `mu`, `f`) and the unknown fit parameters
are the exposure/burial timespans. For a calibration fit (only single
exposure curves), the roles are partially reversed and the known parameters
are `order` and the exposure time, while the unknown fit parameters are
`sigma_phi` and `mu`. Multiple calibration samples are fitted jointly with
per-point `t_exposure` values. This is the most accurate way to fit multiple
samples, because the fit method sees all data at once and can globally try to
minimize the error, instead of only seeing multiple smaller fragments. The GUI
only supports fitting multiple samples for the calibration. However, it is also
possible to use the same approach for the normal dating fit. If the samples
share the same material constants (sigma_phi, mu, etc.) the input data can just
be concatenated to one long sample that can directly be fitted. The fitting
engine also supports differing per-sample material constants, but this requires
scripting against the engine directly.

**Graphical User Interface**

The GUI consists of two windows: The main window and the calibration window.
Each window has its own folder. There is also a `shared` folder with
functionality that is used in both windows. Style settings can be tweaked in
`style_config.py` and `style.qss`.

**Caution**

* As it is now, `bayesian_fit` can only handle normally-distributed known
  parameter uncertainties. However, the calibration results for `sigma_phi` and
  `mu` do not follow a normal distribution, especially not for only few
  calibration samples. In this case, `bayesian_fit` would assume known parameter
  distributions that don't resemble the actual calibration results, which will
  lead to incorrect fitting results.

* The order parameter is subtacted by 1 in the fitting engine, meaning an order
  of 0.0 in the engine is equivalent to the first-order model or an order of
  1.2 is equivalent to the general-order model with an order of 2.2. This makes
  the implementation easier, because now all parameters are always non-negative
  starting from 0.
