from PySide6.QtWidgets import QFileDialog, QMessageBox

def check_bounds_with_message_box(ui, value, bounds, param_name_unicode,
    std=False):
    warning_text \
        = f"{param_name_unicode} must lie between {bounds[0]} and {bounds[1]}."
    if std:
        warning_text = "Standard deviation of " + warning_text

    if not (bounds[0] <= value <= bounds[1]):
        QMessageBox.warning(ui, "Warning", warning_text)
        return False
    return True
