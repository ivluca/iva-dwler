from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QMessageBox, QPushButton, QScrollArea, QSplitter

from iva_downloader.settings import SettingsStore
from iva_downloader.ui import DuplicateUrlsDialog, MainWindow


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
    assert "Preview URLs" not in button_texts
    assert "Add to queue" not in button_texts
    assert "Scan files" not in button_texts
    assert not hasattr(window, "_scan_runner")
    assert window.diag_card.isVisible() is False


def test_panels_stay_fixed_without_horizontal_scroll_or_progress_text_overlap(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)
    window.resize(window.minimumSize())
    qtbot.wait(10)

    splitter = window.findChild(QSplitter, "workspace_splitter")
    scroll = window.findChild(QScrollArea, "SetupScroll")

    assert splitter.handle(1).isEnabled() is False
    assert scroll.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    assert scroll.widget().width() <= scroll.viewport().width()
    assert scroll.horizontalScrollBar().maximum() == 0
    assert window.status_label.text() == "Ready"
    assert window.progress.isTextVisible() is False


def test_advanced_settings_are_always_visible_without_hide_toggle(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)
    window.settings_dialog.show()

    assert window.diag_card.isVisible() is True
    assert window.config_file_input.isVisible() is True
    assert window.extra_arguments_input.isVisible() is True
    assert window.simulate_checkbox.isVisible() is True
    assert window.verbose_checkbox.isVisible() is True
    assert not hasattr(window, "adv_toggle")


def test_settings_contains_updates_advanced_and_language_choices(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)
    dialog = window.settings_dialog

    assert dialog.language_combo.count() == 4
    assert [dialog.language_combo.itemData(i) for i in range(4)] == ["en", "vi", "ja", "zh"]
    assert window.update_button.parent() is not None
    assert window.update_button.parent().parent() is dialog
    assert window.version_label.parent() is window.update_button.parent()
    assert window.diag_card.parent() is not None
    assert dialog.apply_button.text() == "Apply"
    assert dialog.cancel_button.text() == "Cancel"


def test_language_selection_translates_interface_and_persists(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)

    window.settings_dialog.language_combo.setCurrentIndex(1)

    assert window.settings_button.text() == "Settings"
    assert SettingsStore(tmp_path / "settings.json").load().language == "en"

    window.settings_dialog.apply_button.click()

    assert window.settings_button.text() == "Cài đặt"
    assert window.start_button.text() == "Bắt đầu tải"
    assert SettingsStore(tmp_path / "settings.json").load().language == "vi"


def test_cancel_settings_discards_unapplied_changes(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)
    window.settings_dialog.language_combo.setCurrentIndex(1)
    window.simulate_checkbox.setChecked(True)
    QTimer.singleShot(0, window.settings_dialog.reject)

    window._open_settings()

    assert window.settings_button.text() == "Settings"
    assert window.settings_dialog.language_combo.currentData() == "en"
    assert window.simulate_checkbox.isChecked() is False


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


def test_duplicate_dialog_uses_custom_header_and_close_button(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)
    dialog = DuplicateUrlsDialog([("https://example.com/one", 2)], window)
    dialog.show()

    assert dialog.windowFlags() & Qt.WindowType.FramelessWindowHint
    assert dialog.close_button.isVisible()
    qtbot.mouseClick(dialog.close_button, Qt.MouseButton.LeftButton)
    assert dialog.isVisible() is False
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_duplicate_dialog_can_skip_repeated_urls(qtbot, tmp_path, monkeypatch):
    window = make_window(qtbot, tmp_path)
    window.destination_input.setText(str(tmp_path / "downloads"))
    window.urls_input.setPlainText(
        "# keep this note\nhttps://example.com/one\n\nhttps://example.com/two\n"
        " https://example.com/one \nhttps://example.com/one"
    )
    commands = []
    shown = {}
    monkeypatch.setattr(window.runner, "start", lambda command: commands.append(command))

    def choose_skip(dialog):
        shown["items"] = [dialog.duplicate_list.item(i).text() for i in range(dialog.duplicate_list.count())]
        shown["buttons"] = (dialog.skip_button.text(), dialog.download_all_button.text())
        return DuplicateUrlsDialog.SkipDuplicates

    monkeypatch.setattr(DuplicateUrlsDialog, "exec", choose_skip)
    window._start_download()

    assert shown["items"] == ["3 times  •  https://example.com/one"]
    assert shown["buttons"] == ("Skip duplicates", "Download duplicates")
    assert [task.url for task in window.tasks] == ["https://example.com/one", "https://example.com/two"]
    assert window.urls_input.toPlainText() == "# keep this note\nhttps://example.com/one\n\nhttps://example.com/two"
    assert commands[0][-1] == "https://example.com/one"


def test_duplicate_dialog_can_keep_every_occurrence(qtbot, tmp_path, monkeypatch):
    window = make_window(qtbot, tmp_path)
    window.destination_input.setText(str(tmp_path / "downloads"))
    window.urls_input.setPlainText("https://example.com/one\nhttps://example.com/one")
    commands = []
    monkeypatch.setattr(window.runner, "start", lambda command: commands.append(command))
    monkeypatch.setattr(DuplicateUrlsDialog, "exec", lambda dialog: DuplicateUrlsDialog.DownloadAll)

    window._start_download()
    window._on_finished(0)

    assert [task.url for task in window.tasks] == ["https://example.com/one"] * 2
    assert window.urls_input.toPlainText() == "https://example.com/one\nhttps://example.com/one"
    assert len(commands) == 2
    assert window.batch_counts.text() == "2 URLs  •  0 files"


def test_closing_duplicate_dialog_cancels_start(qtbot, tmp_path, monkeypatch):
    window = make_window(qtbot, tmp_path)
    destination = tmp_path / "downloads"
    window.destination_input.setText(str(destination))
    window.urls_input.setPlainText("https://example.com/one\nhttps://example.com/one")
    commands = []
    monkeypatch.setattr(window.runner, "start", lambda command: commands.append(command))
    monkeypatch.setattr(DuplicateUrlsDialog, "exec", lambda dialog: 0)

    window._start_download()

    assert commands == []
    assert window.tasks == []
    assert not destination.exists()
    assert window.status_label.text() == "Ready"


def test_running_state_disables_start(qtbot, tmp_path):
    window = make_window(qtbot, tmp_path)

    window._on_runner_state("running")

    assert window.start_button.isEnabled() is False
    assert window.stop_button.isEnabled() is True
    assert (window.progress.minimum(), window.progress.maximum()) == (0, 1)

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


def test_batch_shows_each_url_and_remaining_count(qtbot, tmp_path, monkeypatch):
    window = make_window(qtbot, tmp_path)
    window.destination_input.setText(str(tmp_path / "downloads"))
    window.urls_input.setPlainText("https://example.com/one\nhttps://example.com/two")
    commands = []
    monkeypatch.setattr(window.runner, "start", lambda command: commands.append(command))

    window._start_download()

    assert len(commands) == 1
    assert commands[0][-1] == "https://example.com/one"
    assert window.batch_counts.text() == "2 URLs  •  0 files"
    assert [task.status for task in window.tasks] == ["Downloading", "Pending"]
    assert window.task_summary.text() == "0 done  •  2 remaining  •  0 failed"
    assert (window.progress.maximum(), window.progress.value()) == (2, 0)
    downloaded_file = tmp_path / "downloads" / "image.jpg"
    downloaded_file.write_bytes(b"image")
    window._handle_output(f"{downloaded_file}\n")
    assert window.tasks[0].files == 1
    assert "1 file" in window.task_list.item(0).text()

    window._on_finished(0)

    assert len(commands) == 2
    assert commands[1][-1] == "https://example.com/two"
    assert [task.status for task in window.tasks] == ["Done", "Downloading"]
    assert window.task_summary.text() == "1 done  •  1 remaining  •  0 failed"
    assert window.progress.value() == 1

    window._on_finished(1)

    assert [task.status for task in window.tasks] == ["Done", "Failed"]
    assert window.task_summary.text() == "1 done  •  0 remaining  •  1 failed"
    assert window.progress.value() == 2
    assert window.status_label.text() == "Download complete. 1 done, 1 failed; 1 file downloaded."


def test_stopping_batch_leaves_other_urls_pending(qtbot, tmp_path, monkeypatch):
    window = make_window(qtbot, tmp_path)
    window.destination_input.setText(str(tmp_path / "downloads"))
    window.urls_input.setPlainText("https://example.com/one\nhttps://example.com/two")
    commands = []
    monkeypatch.setattr(window.runner, "start", lambda command: commands.append(command))

    window._start_download()
    window._stop_download()
    window._on_finished(-1)

    assert len(commands) == 1
    assert [task.status for task in window.tasks] == ["Stopped", "Pending"]
    assert window.task_summary.text() == "0 done  •  1 remaining  •  0 failed"


def test_transfer_stats_format_bytes():
    from iva_downloader.ui import MainWindow

    assert MainWindow._format_bytes(900) == "900 B"
    assert MainWindow._format_bytes(1500) == "1.5 KB"


def test_file_output_updates_download_count_and_transfer_size(qtbot, tmp_path):
    import time

    from iva_downloader.models import DownloadSettings

    window = make_window(qtbot, tmp_path)
    destination = tmp_path / "downloads"
    destination.mkdir()
    file_path = destination / "image.jpg"
    file_path.write_bytes(b"x" * 1500)
    window.destination_input.setText(str(destination))
    window._active_settings = DownloadSettings(destination=str(destination))
    window._run_started_at = time.monotonic()

    window._handle_output(f"{file_path}\n")

    assert window.downloaded == 1
    assert window.downloaded_bytes == 1500
    assert "1 file" in window.batch_counts.text()
    assert "1.5 KB downloaded" in window.transfer_stats.text()
