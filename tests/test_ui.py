from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox, QPushButton, QSplitter

from iva_downloader.settings import SettingsStore
from iva_downloader.ui import MainWindow


def make_window(qtbot, tmp_path):
    window = MainWindow(
        settings_store=SettingsStore(tmp_path / "settings.json"),
        check_gallery_dl=False,
    )
    qtbot.addWidget(window)
    window.show()
    return window


def test_main_window_uses_split_workspace_and_english_primary_actions(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)

    splitter = window.findChild(QSplitter, "workspace_splitter")
    button_texts = {button.text() for button in window.findChildren(QPushButton)}

    assert window.windowTitle() == "IVA Downloader"
    assert window.brand_label.text() == "IVA Downloader"
    assert splitter is not None and splitter.count() == 2
    assert {"Paste", "Import file", "Clear", "Start download", "Stop", "Clear log"} <= button_texts
    assert "Scan files" not in button_texts
    assert not hasattr(window, "_scan_runner")
    assert window.diag_card.isVisible() is False


def test_advanced_toggle_reveals_entire_diagnostics_card(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)

    qtbot.mouseClick(window.adv_toggle, Qt.MouseButton.LeftButton)

    assert window.diag_card.isVisible() is True
    assert window.config_file_input.isVisible() is True
    assert window.extra_arguments_input.isVisible() is True
    assert window.simulate_checkbox.isVisible() is True
    assert window.verbose_checkbox.isVisible() is True


def test_start_validation_is_inline_and_does_not_start_runner(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)
    window.urls_input.clear()
    window.destination_input.clear()

    qtbot.mouseClick(window.start_button, Qt.MouseButton.LeftButton)

    assert window.urls_error.text() == "Add at least one URL."
    assert window.destination_error.text() == "Choose an output folder."
    assert window.urls_error.isVisible()
    assert window.destination_error.isVisible()
    assert window.runner.is_running is False


def test_running_state_disables_start_and_uses_busy_progress(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)

    window._on_runner_state("running")

    assert window.start_button.isEnabled() is False
    assert window.stop_button.isEnabled() is True
    assert (window.progress.minimum(), window.progress.maximum()) == (0, 0)

    window._on_runner_state("idle")

    assert window.start_button.isEnabled() is True
    assert window.stop_button.isEnabled() is False
    assert (window.progress.minimum(), window.progress.maximum()) == (0, 1)



def test_close_waits_for_running_process_to_stop(qtbot, tmp_path, monkeypatch):
    import sys

    window = make_window(qtbot, tmp_path)
    window.runner.kill_timeout_ms = 50
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    window.runner.start([sys.executable, "-c", "import time; time.sleep(10)"])
    qtbot.waitUntil(lambda: window.runner.is_running, timeout=1000)

    with qtbot.waitSignal(window.runner.finished, timeout=3000):
        window.close()
        assert window.isVisible() is True

    qtbot.waitUntil(lambda: not window.isVisible(), timeout=1000)


def test_default_output_uses_user_downloads(tmp_path):
    from iva_downloader import ui

    result = ui.default_output_directory(home=tmp_path)

    assert result == tmp_path / "Downloads" / "IVA Downloader"


def test_cookie_authentication_uses_file_source_only(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)

    assert window.cookie_file_input.placeholderText() == "Choose a Netscape-format cookies.txt file"
    assert not hasattr(window, "browser_combo")
    assert not hasattr(window, "cookie_source_combo")


def test_concurrent_downloads_control_is_not_exposed(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)

    assert not hasattr(window, "jobs_input")
    assert window._collect_settings().jobs == ""


def test_window_typography_uses_medium_weight(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)

    assert window.font().weight() == QFont.Weight.Medium
    assert window.brand_label.font().weight() == QFont.Weight.Medium
    assert window.activity_title.font().weight() == QFont.Weight.Medium
