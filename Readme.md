**Python Time Machine**

The Python Time Machine consists of two parts: The fitting engine and the
graphical user interface. The fitting engine is located in the
`fitting_engine` folder, the user interface in the `gui` folder. The GUI is
started by running `main.py` (optional `--verbose` flag for console output).

**Fitting Engine**

The `fitcore` folder hosts functionality that is not OSL-specific but could
be used for all fitting purposes. All files that sit directly in the
`fitting_engine` folder are OSL-specific, like `models.py` which implements
the mathematical model functions. The fitting engine exposes different
methods that can be used for a fit.

* `easy_fit`:  
  A normal SciPy least-squares fit that finds the maximum likelihood values
  for the fit parameters given a model function and input data. The error
  estimation is omitted because it is not accurate for highly non-linear
  functions, like the luminescence model functions. `easy_fit` always
  requires an initial guess, because it can only find the nearest local
  minimum.

* `get_initial_guess`:  
  Uses SciPy's `differential_evolution` to find the global minimum, which
  can serve as an initial guess for `easy_fit`. In theory, it is not
  guaranteed that the algorithm always finds the global minimum. The
  parameter bounds are very important for the initial guess finder because
  they constrain the search space.

* `bootstrap_fit`:  
  Runs `easy_fit` many times resampling input data to obtain a probability
  distribution of the best fit parameters and thus estimating the
  uncertainties. It can also handle uncertain known parameters, by
  additionally perturbing them according to the given standard deviation.
  The bootstrap results can become unstable when there are only a few data
  points that heavily influence the fit result, which is the case for a
  bleaching front curve. Therefore, the bootstrap fit should only serve as
  an estimator.

* `bayesian_fit`:  
  Uses MCMC (Markov chain Monte Carlo) from the PyMC module to produce any
  number of random samples from the parameter space that follow the true
  probability distribution. Thus, with a large enough number of samples one
  can obtain the probability distribution (posterior) for each parameter and
  calculate confidence intervals. However, in order to work efficiently it
  needs prior knowledge about each parameter to constrain the parameter
  space.

* `full_fit`:  
  The `full_fit` function first finds an initial guess with
  `get_initial_guess` which is needed for `bootstrap_fit`. Then it uses
  `bootstrap_fit` to estimate the uncertainties of the fit parameters and
  uses the results as priors for `bayesian_fit`. It is very important that
  the priors are not too tight, since this would bias the result. Therefore,
  the standard deviation of the bootstrap result is doubled to always ensure
  conservative guesses, but still constrain the MCMC search space.

* `get_event_ages`:  
  To obtain the age of an event it's not accurate to simply add all
  timespans of the following events, especially not for the confidence
  intervals. `get_event_ages` calculates the true event ages based on the
  posterior samples obtained from `bayesian_fit`.

For a normal fit the known fitting parameters are the material properties of
the rock (`order`, `sigma_phi`, `mu`, `f`) and the unknown fit parameters
are the exposure/burial timespans. For a calibration fit (only single
exposure curves), the roles are partially reversed and the known parameters
are `order` and the exposure time, while the unknown fit parameters are
`sigma_phi` and `mu`. Multiple calibration samples are fitted jointly with
per-point `t_exposure` values. This is the most accurate way to fit multiple
calibration samples, because the fit method sees all data at once and can
globally try to minimize the error.

**Graphical User Interface**

The GUI consists of two windows: The main window and the calibration window.
Each window has its own folder. There is also a `shared` folder with
functionality that is used in both windows. Style settings can be tweaked in
`style_config.py` and `style.qss`.

** 