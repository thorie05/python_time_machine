import numpy as np


def get_event_ages(param_names, posterior_samples):
    """A function that calculates event ages.

    Takes the names of the time span fit parameters from "oldest" to "youngest"
    (t_exposure_1, t_burial_1, t_exposure_2, ...) and calculates the total
    elapsed time since the beginning of each of these time spans. The first
    event in this case would be the first exposure, the second event the
    subsequent burial, etc. The normal fitting with the functions in models.py
    only yield time span results, not ages. The ages are approximately equal to
    the sum of the best fits, but not exactly, especially for the confidence
    ranges. To obtain correct results, only fit results coming from the same
    sample need to be added, as done in this function. The leading t_ is removed
    from the given parameter names and instead _age is appended in in the result
    dicts.

    Args:
        param_names (List(str)): A list of the parameter names sorted from
            "oldest" to "youngest".
        posterior_samples (dict(str: numpy.ndarray))
    Returns:
        Tuple(dict(str: float), dict(str: numpy.ndarray))
    """

    event_ages = {}
    event_ages_posterior_samples = {}

    cumulative_sum = np.zeros(posterior_samples[param_names[0]].shape)

    for param_name in reversed(param_names):
        # cumulatively add the timespans belonging together from each sample
        cumulative_sum += posterior_samples[param_name]
        median = np.median(cumulative_sum)
        lower, upper = np.percentile(cumulative_sum, [15.865, 84.135])

        new_param_name = "age_" + param_name[2:]
        event_ages[new_param_name] \
            = (float(median), (float(lower), float(upper)))
        event_ages_posterior_samples[new_param_name] = cumulative_sum.copy()

    return (event_ages, event_ages_posterior_samples)
