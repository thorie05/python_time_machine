from fit import fit
import numpy as np
import matplotlib.pyplot as plt
import models

order = 1
sigma_phi = 5
mu = 5
t_expo_1 = 300

x_data = np.linspace(0, 3, 30)
y_data = models.expo(x_data, order, sigma_phi, mu, t_expo_1)

perturbation = np.random.normal(loc=0.0, scale=0.1, size=x_data.shape)
y_data = y_data + perturbation
y_data = np.clip(y_data, 0, 1)

t_expo_1_fit = fit(x_data, y_data, models.expo, {"order": order, "sigma_phi": \
    sigma_phi, "mu": mu}, {"t_expo_1": 0})["t_expo_1"]

x_fit = np.linspace(0, 3, 100)
y_fit = models.expo(x_fit, order, sigma_phi, mu, t_expo_1_fit)

print(t_expo_1_fit)

plt.scatter(x_data, y_data)
plt.plot(x_fit, y_fit, color="r")
plt.show()
