from PySide6.QtWidgets import QFileDialog, QMessageBox

class BoundCheckerWithMessageBox:
    def __init__(self, engine, ui):
        self.engine = engine
        self.ui = ui

    def _check(self, value, bounds, warning_text):
        if not (bounds[0] <= value <= bounds[1]):

            QMessageBox.warning(self.ui, "Warning", warning_text)
            return False
        return True

    def check_order(self, order):
        return self._check(order, self.engine.bounds.order,
            f"order must lie between {self.engine.bounds.order[0] + 1} "
            f"and {self.engine.bounds.order[1] + 1}.")

    def check_order_std(self, order_std):
        return self._check(order_std, self.engine.bounds.order_std,
            f"Standard deviation of order must lie between "
            f"{self.engine.bounds.order_std[0]} and "
            f"{self.engine.bounds.order_std[1]}.")

    def check_sigma_phi(self, sigma_phi):
        return self._check(sigma_phi, self.engine.bounds.sigma_phi,
            f"<span style='text-decoration: overline;'>σφ</span><sub>0</sub> "
            f"must lie between {self.engine.bounds.sigma_phi[0]} and "
            f"{self.engine.bounds.sigma_phi[1]}.")

    def check_sigma_phi_std(self, sigma_phi_std):
        return self._check(sigma_phi_std, self.engine.bounds.sigma_phi_std,
            f"Standard deviation of <span style='text-decoration: "
            f"overline;'>σφ</span><sub>0</sub> must lie between "
            f"{self.engine.bounds.sigma_phi_std[0]} and "
            f"{self.engine.bounds.sigma_phi_std[1]}.")

    def check_mu(self, mu):
        return self._check(mu, self.engine.bounds.mu,
            f"µ must lie between {self.engine.bounds.mu[0]} and "
            f"{self.engine.bounds.mu[1]}.")

    def check_mu_std(self, mu_std):
        return self._check(mu_std, self.engine.bounds.mu_std,
            f"Standard deviation of µ must lie between "
            f"{self.engine.bounds.mu_std[0]} and "
            f"{self.engine.bounds.mu_std[1]}.")

    def check_f(self, f):
        return self._check(f, self.engine.bounds.f,
            f"f must lie between {self.engine.bounds.f[0]} and "
            f"{self.engine.bounds.f[1]}.")

    def check_f_std(self, f_std):
        return self._check(f_std, self.engine.bounds.f_std,
            f"Standard deviation of f must lie between "
            f"{self.engine.bounds.f_std[0]} and "
            f"{self.engine.bounds.f_std[1]}.")
