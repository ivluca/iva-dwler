import os
import shlex
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, QProcess, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .command import build_command, gallery_dl_base_command
from .models import DownloadSettings, find_duplicate_urls, validate_settings
from .resources import icon, load_app_font
from .runner import DownloadRunner
from .settings import SettingsStore


APP_NAME = "IVA Downloader"

TRANSLATIONS = {
    "vi": {
        "Settings": "Cài đặt", "Check for updates": "Kiểm tra cập nhật", "Language": "Ngôn ngữ", "Advanced": "Nâng cao", "Updates": "Cập nhật", "Apply": "Áp dụng", "Cancel": "Hủy",
        "Hide advanced": "Ẩn nâng cao", "URLs": "Đường dẫn URL", "Add one URL per line. Lines beginning with # are ignored.": "Nhập mỗi URL trên một dòng. Dòng bắt đầu bằng # sẽ được bỏ qua.",
        "Paste": "Dán", "Import file": "Nhập tệp", "Clear": "Xóa", "Destination": "Thư mục lưu", "Choose where downloaded files are saved.": "Chọn nơi lưu tệp đã tải.",
        "Cookie source": "Nguồn cookie", "Choose a cookies.txt file only when a site requires authentication.": "Chỉ chọn tệp cookies.txt khi trang web yêu cầu xác thực.",
        "Choose an output folder": "Chọn thư mục lưu", "Choose a Netscape-format cookies.txt file": "Chọn tệp cookies.txt định dạng Netscape", "Browse": "Duyệt",
        "Diagnostics": "Chẩn đoán", "Optional gallery-dl config and extra flags.": "Tệp cấu hình gallery-dl và tùy chọn bổ sung.", "Optional gallery-dl config file": "Tệp cấu hình gallery-dl (tùy chọn)",
        "Example: --no-mtime": "Ví dụ: --no-mtime", "Pass additional gallery-dl command-line arguments.": "Thêm tham số dòng lệnh cho gallery-dl.",
        "Simulate only — preview files without downloading": "Chạy thử — xem trước mà không tải tệp", "Verbose logging — show detailed HTTP activity": "Nhật ký chi tiết — hiển thị hoạt động HTTP",
        "Activity": "Hoạt động", "Ready": "Sẵn sàng", "Tasks": "Tác vụ", "Start download": "Bắt đầu tải", "Stop": "Dừng", "Clear log": "Xóa nhật ký",
        "Download activity will appear here.": "Hoạt động tải xuống sẽ hiển thị tại đây.", "Check for updates": "Kiểm tra cập nhật",
    },
    "ja": {
        "Settings": "設定", "Check for updates": "更新を確認", "Language": "言語", "Advanced": "詳細設定", "Updates": "更新", "Apply": "適用", "Cancel": "キャンセル",
        "URLs": "URL", "Add one URL per line. Lines beginning with # are ignored.": "URLを1行に1つ入力してください。#で始まる行は無視されます。", "Paste": "貼り付け", "Import file": "ファイルを読み込む", "Clear": "クリア",
        "Destination": "保存先", "Choose where downloaded files are saved.": "ダウンロードしたファイルの保存先を選択します。", "Cookie source": "Cookie", "Choose a cookies.txt file only when a site requires authentication.": "認証が必要な場合のみcookies.txtを選択してください。",
        "Choose an output folder": "保存先フォルダーを選択", "Choose a Netscape-format cookies.txt file": "Netscape形式のcookies.txtを選択", "Browse": "参照", "Diagnostics": "詳細オプション", "Optional gallery-dl config and extra flags.": "gallery-dl設定ファイルと追加オプション（任意）。",
        "Optional gallery-dl config file": "gallery-dl設定ファイル（任意）", "Example: --no-mtime": "例: --no-mtime", "Simulate only — preview files without downloading": "シミュレーション — ダウンロードせずに確認", "Verbose logging — show detailed HTTP activity": "詳細ログ — HTTP通信を表示",
        "Activity": "アクティビティ", "Ready": "準備完了", "Tasks": "タスク", "Start download": "ダウンロード開始", "Stop": "停止", "Clear log": "ログを消去", "Download activity will appear here.": "ダウンロード状況がここに表示されます。",
    },
    "zh": {
        "Settings": "设置", "Check for updates": "检查更新", "Language": "语言", "Advanced": "高级", "Updates": "更新", "Apply": "应用", "Cancel": "取消",
        "URLs": "链接", "Add one URL per line. Lines beginning with # are ignored.": "每行输入一个 URL。以 # 开头的行将被忽略。", "Paste": "粘贴", "Import file": "导入文件", "Clear": "清除",
        "Destination": "保存位置", "Choose where downloaded files are saved.": "选择下载文件的保存位置。", "Cookie source": "Cookie 来源", "Choose a cookies.txt file only when a site requires authentication.": "仅在网站需要身份验证时选择 cookies.txt 文件。",
        "Choose an output folder": "选择输出文件夹", "Choose a Netscape-format cookies.txt file": "选择 Netscape 格式的 cookies.txt 文件", "Browse": "浏览", "Diagnostics": "诊断", "Optional gallery-dl config and extra flags.": "可选的 gallery-dl 配置和额外参数。",
        "Optional gallery-dl config file": "可选的 gallery-dl 配置文件", "Example: --no-mtime": "例如：--no-mtime", "Simulate only — preview files without downloading": "仅模拟 — 预览文件，不进行下载", "Verbose logging — show detailed HTTP activity": "详细日志 — 显示 HTTP 活动",
        "Activity": "活动", "Ready": "就绪", "Tasks": "任务", "Start download": "开始下载", "Stop": "停止", "Clear log": "清除日志", "Download activity will appear here.": "下载活动将显示在这里。",
    },
}


def default_output_directory(home: Path | None = None) -> Path:
    home = home or Path.home()
    return home / "Downloads" / APP_NAME


DEFAULT_OUTPUT = default_output_directory()


@dataclass
class DownloadTask:
    url: str
    status: str = "Pending"
    files: int = 0


class DuplicateUrlsDialog(QDialog):
    SkipDuplicates = 1
    DownloadAll = 2

    def __init__(self, duplicates: list[tuple[str, int]], parent: QWidget):
        super().__init__(parent)
        self.setObjectName("DuplicateUrlsDialog")
        self.setWindowTitle("Duplicate URLs")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setMinimumWidth(540)
        self._drag_offset: QPoint | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(10)
        self.title_bar = QFrame()
        self.title_bar.setObjectName("DialogTitleBar")
        self.title_bar.installEventFilter(self)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Duplicate URLs")
        title.setObjectName("DialogTitle")
        title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        title_layout.addWidget(title)
        title_layout.addStretch()
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("DialogCloseButton")
        self.close_button.setAccessibleName("Close dialog")
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.reject)
        title_layout.addWidget(self.close_button)
        layout.addWidget(self.title_bar)
        divider = QFrame()
        divider.setObjectName("DialogDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider)
        description = QLabel("These URLs appear more than once in this download:")
        description.setWordWrap(True)
        layout.addWidget(description)
        self.duplicate_list = QListWidget()
        self.duplicate_list.setObjectName("DuplicateList")
        self.duplicate_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for url, count in duplicates:
            item = QListWidgetItem(f"{count} times  •  {url}")
            item.setToolTip(url)
            self.duplicate_list.addItem(item)
        layout.addWidget(self.duplicate_list)
        explanation = QLabel("Skip duplicates removes repeated URL lines and downloads each URL once.")
        explanation.setWordWrap(True)
        explanation.setObjectName("Muted")
        layout.addWidget(explanation)
        actions = QHBoxLayout()
        actions.addStretch()
        self.skip_button = QPushButton("Skip duplicates")
        self.skip_button.setDefault(True)
        self.skip_button.clicked.connect(lambda: self.done(self.SkipDuplicates))
        actions.addWidget(self.skip_button)
        self.download_all_button = QPushButton("Download duplicates")
        self.download_all_button.clicked.connect(lambda: self.done(self.DownloadAll))
        actions.addWidget(self.download_all_button)
        layout.addLayout(actions)

    def eventFilter(self, watched, event) -> bool:
        if watched is self.title_bar:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                return True
            if event.type() == QEvent.Type.MouseMove and self._drag_offset is not None:
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                return True
            if event.type() == QEvent.Type.MouseButtonRelease:
                self._drag_offset = None
                return True
        return super().eventFilter(watched, event)


class SettingsDialog(QDialog):
    LANGUAGES = [("English", "en"), ("Tiếng Việt", "vi"), ("日本語", "ja"), ("中文", "zh")]

    def __init__(self, advanced_card: QWidget, version_label: QLabel, update_button: QPushButton, language: str, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setObjectName("SettingsDialog")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        title = QLabel("Settings")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        language_group = QGroupBox("Language")
        language_layout = QVBoxLayout(language_group)
        self.language_combo = QComboBox()
        for label, code in self.LANGUAGES:
            self.language_combo.addItem(label, code)
        index = self.language_combo.findData(language)
        self.language_combo.setCurrentIndex(max(index, 0))
        language_layout.addWidget(self.language_combo)
        layout.addWidget(language_group)
        advanced_group = QGroupBox("Advanced")
        advanced_layout = QVBoxLayout(advanced_group)
        advanced_card.setVisible(True)
        advanced_layout.addWidget(advanced_card)
        layout.addWidget(advanced_group)
        update_group = QGroupBox("Updates")
        update_layout = QVBoxLayout(update_group)
        update_row = QHBoxLayout()
        update_row.addWidget(version_label)
        update_row.addStretch()
        update_row.addWidget(update_button)
        update_layout.addLayout(update_row)
        layout.addWidget(update_group)
        layout.addStretch()
        actions = QHBoxLayout()
        actions.addStretch()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        actions.addWidget(self.cancel_button)
        self.apply_button = QPushButton("Apply")
        self.apply_button.setDefault(True)
        actions.addWidget(self.apply_button)
        layout.addLayout(actions)
        self.setMinimumWidth(440)


class MainWindow(QMainWindow):
    def __init__(self, settings_store: SettingsStore | None = None, check_gallery_dl: bool = True):
        super().__init__()
        self.settings_store = settings_store or SettingsStore()
        self.runner = DownloadRunner(self)
        self.runner.output.connect(self._handle_output)
        self.runner.state_changed.connect(self._on_runner_state)
        self.runner.finished.connect(self._on_finished)
        self.downloaded = 0
        self.skipped = 0
        self.downloaded_bytes = 0
        self._counted_files: set[Path] = set()
        self.tasks: list[DownloadTask] = []
        self._active_task_index: int | None = None
        self._processed_tasks = 0
        self._batch_total = 0
        self._run_started_at = 0.0
        self._active_settings: DownloadSettings | None = None
        self._line_buffer = ""
        self._stopped_by_user = False
        self._update_mode = False
        self._close_after_stop = False
        self._version_process: QProcess | None = None
        self._brand_family = load_app_font()
        base_font = QFont(self.font())
        if self._brand_family:
            base_font.setFamily(self._brand_family)
        base_font.setWeight(QFont.Weight.Medium)
        self.setFont(base_font)

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(icon("download_for_offline"))
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)
        self._build_ui()
        self._capture_ui_text()
        self._applied_settings = self.settings_store.load()
        self._apply_settings(self._applied_settings)
        self._translate_interface()
        self._apply_style()
        if check_gallery_dl:
            QTimer.singleShot(250, self._check_gallery_dl)

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("AppRoot")
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        header = QHBoxLayout()
        self.brand_label = QLabel(APP_NAME)
        self.brand_label.setObjectName("Brand")
        if self._brand_family:
            self.brand_label.setFont(QFont(self._brand_family, 25, QFont.Weight.Medium))
        header.addWidget(self.brand_label)
        header.addStretch()
        self.version_label = QLabel("Checking gallery-dl…")
        self.version_label.setObjectName("Muted")
        self.settings_button = self._button("Settings", "tune", self._open_settings)
        self.settings_button.setProperty("secondary", True)
        header.addWidget(self.settings_button)
        root.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("workspace_splitter")
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_setup_panel())
        splitter.addWidget(self._build_activity_panel())
        splitter.setStretchFactor(0, 44)
        splitter.setStretchFactor(1, 56)
        splitter.setSizes([500, 640])
        splitter.handle(1).setEnabled(False)
        root.addWidget(splitter, 1)
        self.setCentralWidget(central)
        self.update_button = self._button("Check for updates", "system_update_alt", self._update_gallery_dl)
        self.update_button.setProperty("secondary", True)
        self.settings_dialog = SettingsDialog(self.diag_card, self.version_label, self.update_button, "en", self)
        self.settings_dialog.apply_button.clicked.connect(self._apply_settings_changes)

    def _build_setup_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setObjectName("SetupScroll")
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(12)

        urls_card, urls_layout = self._card("URLs", "Add one URL per line. Lines beginning with # are ignored.", required=True)
        self.urls_input = QPlainTextEdit()
        self.urls_input.setObjectName("UrlsInput")
        self.urls_input.setPlaceholderText("https://example.com/gallery")
        self.urls_input.setMinimumHeight(132)
        urls_layout.addWidget(self.urls_input)
        url_edit_actions = QHBoxLayout()
        url_edit_actions.addWidget(self._button("Paste", "content_paste", self._paste_urls, compact=True))
        url_edit_actions.addWidget(self._button("Import file", "file_open", self._import_urls, compact=True))
        url_edit_actions.addStretch()
        url_edit_actions.addWidget(self._button("Clear", "delete_sweep", self.urls_input.clear, compact=True))
        urls_layout.addLayout(url_edit_actions)
        self.urls_error = self._error_label()
        urls_layout.addWidget(self.urls_error)
        layout.addWidget(urls_card)

        destination_card, destination_layout = self._card("Destination", "Choose where downloaded files are saved.", required=True)
        destination_row = QHBoxLayout()
        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("Choose an output folder")
        destination_row.addWidget(self.destination_input, 1)
        browse = self._icon_button("folder_open", "Browse", self._choose_destination)
        open_folder = self._icon_button("open_in_new", "Open folder", self._open_destination)
        destination_row.addWidget(browse)
        destination_row.addWidget(open_folder)
        destination_layout.addLayout(destination_row)
        self.destination_error = self._error_label()
        destination_layout.addWidget(self.destination_error)
        layout.addWidget(destination_card)

        auth_card, auth_layout = self._card("Cookie source", "Choose a cookies.txt file only when a site requires authentication.")
        file_row = QHBoxLayout()
        self.cookie_file_input = QLineEdit()
        self.cookie_file_input.setPlaceholderText("Choose a Netscape-format cookies.txt file")
        file_row.addWidget(self.cookie_file_input, 1)
        file_row.addWidget(self._icon_button("folder_open", "Browse", self._choose_cookie_file))
        auth_layout.addLayout(file_row)
        layout.addWidget(auth_card)

        self.diag_card, diag_layout = self._card("Diagnostics", "Optional gallery-dl config and extra flags.")
        config_row = QHBoxLayout()
        self.config_file_input = QLineEdit()
        self.config_file_input.setPlaceholderText("Optional gallery-dl config file")
        config_row.addWidget(self.config_file_input, 1)
        config_row.addWidget(self._icon_button("folder_open", "Browse", self._choose_config_file))
        diag_layout.addLayout(config_row)
        self.extra_arguments_input = self._line("Example: --no-mtime")
        self.extra_arguments_input.setToolTip("Pass additional gallery-dl command-line arguments.")
        self.extra_arguments_error = self._error_label()
        diag_layout.addWidget(self.extra_arguments_input)
        diag_layout.addWidget(self.extra_arguments_error)

        self.simulate_checkbox = QCheckBox("Simulate only — preview files without downloading")
        self.verbose_checkbox = QCheckBox("Verbose logging — show detailed HTTP activity")
        self.simulate_checkbox.setToolTip("Passes --simulate to gallery-dl. No files are written to disk.")
        self.verbose_checkbox.setToolTip("Passes -v to gallery-dl. Useful for debugging errors.")
        diag_layout.addWidget(self.simulate_checkbox)
        diag_layout.addWidget(self.verbose_checkbox)

        self.diag_card.setVisible(True)
        layout.addWidget(self.diag_card)

        layout.addStretch()
        scroll.setWidget(body)
        return scroll



    def _build_activity_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("ActivityPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title_row = QHBoxLayout()
        self.activity_title = QLabel("Activity")
        self.activity_title.setObjectName("SectionTitle")
        if self._brand_family:
            self.activity_title.setFont(QFont(self._brand_family, 16, QFont.Weight.Medium))
        title_row.addWidget(self.activity_title)
        title_row.addStretch()
        self.batch_counts = QLabel("0 URLs  •  0 files")
        self.batch_counts.setObjectName("Pill")
        title_row.addWidget(self.batch_counts)
        layout.addLayout(title_row)
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("Status")
        layout.addWidget(self.status_label)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.transfer_stats = QLabel("0 B downloaded  •  0 B/s")
        self.transfer_stats.setObjectName("Muted")
        layout.addWidget(self.transfer_stats)
        self.tasks_container = QWidget()
        tasks_layout = QVBoxLayout(self.tasks_container)
        tasks_layout.setContentsMargins(0, 0, 0, 0)
        tasks_layout.setSpacing(6)
        task_heading = QHBoxLayout()
        task_heading.addWidget(QLabel("Tasks"))
        task_heading.addStretch()
        self.task_summary = QLabel("0 done  •  0 remaining  •  0 failed")
        self.task_summary.setObjectName("Pill")
        task_heading.addWidget(self.task_summary)
        tasks_layout.addLayout(task_heading)
        self.task_list = QListWidget()
        self.task_list.setObjectName("TaskList")
        self.task_list.setMaximumHeight(170)
        self.task_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tasks_layout.addWidget(self.task_list)
        self.tasks_container.setVisible(False)
        layout.addWidget(self.tasks_container)
        self.log = QTextEdit()
        self.log.setObjectName("Log")
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Download activity will appear here.")
        self.log.setFont(QFont(self._brand_family, 10))
        layout.addWidget(self.log, 1)
        actions = QHBoxLayout()
        self.start_button = self._button("Start download", "download", self._start_download)
        self.start_button.setObjectName("PrimaryButton")
        self.stop_button = self._button("Stop", "stop_circle", self._stop_download)
        self.stop_button.setEnabled(False)
        self.clear_log_button = self._button("Clear log", "delete_sweep", self.log.clear)
        self.clear_log_button.setProperty("secondary", True)
        actions.addWidget(self.start_button)
        actions.addWidget(self.stop_button)
        actions.addStretch()
        actions.addWidget(self.clear_log_button)
        layout.addLayout(actions)
        return panel

    def _card(self, title: str, description: str, required: bool = False) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        heading_row = QHBoxLayout()
        heading_row.setSpacing(4)
        heading = QLabel(title)
        heading.setObjectName("CardTitle")
        if self._brand_family:
            heading.setFont(QFont(self._brand_family, 15, QFont.Weight.Medium))
        heading_row.addWidget(heading)
        if required:
            asterisk = QLabel("*")
            asterisk.setObjectName("RequiredStar")
            if self._brand_family:
                asterisk.setFont(QFont(self._brand_family, 15, QFont.Weight.Medium))
            heading_row.addWidget(asterisk)
        heading_row.addStretch()
        layout.addLayout(heading_row)
        subtitle = QLabel(description)
        subtitle.setWordWrap(True)
        subtitle.setObjectName("Muted")
        layout.addWidget(subtitle)
        return card, layout

    def _button(self, text: str, icon_name: str, callback, compact: bool = False) -> QPushButton:
        button = QPushButton(text)
        button.setIcon(icon(icon_name))
        button.setIconSize(QSize(18, 18))
        button.clicked.connect(callback)
        if compact:
            button.setProperty("compact", True)
        return button

    def _icon_button(self, icon_name: str, tooltip: str, callback) -> QPushButton:
        button = QPushButton()
        button.setIcon(icon(icon_name))
        button.setIconSize(QSize(19, 19))
        button.setToolTip(tooltip)
        button.setAccessibleName(tooltip)
        button.setFixedWidth(38)
        button.clicked.connect(callback)
        return button

    def _line(self, placeholder: str) -> QLineEdit:
        widget = QLineEdit()
        widget.setPlaceholderText(placeholder)
        return widget

    def _error_label(self) -> QLabel:
        label = QLabel()
        label.setObjectName("FieldError")
        label.setVisible(False)
        label.setWordWrap(True)
        return label

    def _open_settings(self) -> None:
        self.settings_dialog.exec()
        if self.settings_dialog.result() != QDialog.DialogCode.Accepted:
            self._apply_settings(self._applied_settings)

    def _apply_settings_changes(self) -> None:
        settings = self._collect_settings()
        try:
            self.settings_store.save(settings)
        except OSError as error:
            QMessageBox.warning(self, APP_NAME, f"Could not apply settings: {error}")
            return
        self._applied_settings = settings
        self._translate_interface()
        self.settings_dialog.accept()

    def _capture_ui_text(self) -> None:
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QLabel, QPushButton, QCheckBox, QGroupBox)):
                widget.setProperty("englishText", widget.text() if hasattr(widget, "text") else widget.title())
            if isinstance(widget, (QLineEdit, QPlainTextEdit, QTextEdit)):
                widget.setProperty("englishPlaceholder", widget.placeholderText())

    def _translate_interface(self) -> None:
        language = self.settings_dialog.language_combo.currentData()
        translations = TRANSLATIONS.get(language, {})
        for widget in self.findChildren(QWidget):
            original = widget.property("englishText")
            if original is not None:
                translated = translations.get(original, original)
                if isinstance(widget, QGroupBox):
                    widget.setTitle(translated)
                elif hasattr(widget, "setText"):
                    widget.setText(translated)
            placeholder = widget.property("englishPlaceholder")
            if placeholder:
                placeholder_map = translations.get(placeholder, placeholder)
                widget.setPlaceholderText(placeholder_map)
        self.settings_dialog.setWindowTitle(translations.get("Settings", "Settings"))
        self.setWindowTitle(APP_NAME)

    def _collect_urls(self) -> list[str]:
        return [line.strip() for line in self.urls_input.toPlainText().splitlines() if line.strip() and not line.lstrip().startswith("#")]

    def _remove_duplicate_url_lines(self) -> None:
        seen: set[str] = set()
        kept: list[str] = []
        for line in self.urls_input.toPlainText().splitlines():
            url = line.strip()
            if url and not line.lstrip().startswith("#"):
                if url in seen:
                    continue
                seen.add(url)
            kept.append(line)
        self.urls_input.setPlainText("\n".join(kept))

    def _collect_settings(self) -> DownloadSettings:
        return DownloadSettings(
            destination=self.destination_input.text().strip(),
            cookie_file=self.cookie_file_input.text().strip(),
            config_file=self.config_file_input.text().strip(),
            jobs="",
            simulate=self.simulate_checkbox.isChecked(),
            verbose=self.verbose_checkbox.isChecked(),
            extra_arguments=self.extra_arguments_input.text().strip(),
            language=self.settings_dialog.language_combo.currentData() if hasattr(self, "settings_dialog") else "en",
        )

    def _apply_settings(self, settings: DownloadSettings) -> None:
        self.destination_input.setText(settings.destination or str(DEFAULT_OUTPUT))
        self.cookie_file_input.setText(settings.cookie_file)
        self.config_file_input.setText(settings.config_file)
        self.simulate_checkbox.setChecked(settings.simulate)
        self.verbose_checkbox.setChecked(settings.verbose)
        self.extra_arguments_input.setText(settings.extra_arguments)
        index = self.settings_dialog.language_combo.findData(settings.language) if hasattr(self, "settings_dialog") else -1
        if index >= 0:
            self.settings_dialog.language_combo.setCurrentIndex(index)

    def _clear_errors(self) -> None:
        for label in (
            self.urls_error,
            self.destination_error,
            self.extra_arguments_error,
        ):
            label.clear()
            label.setVisible(False)

    def _show_errors(self, errors: dict[str, str]) -> None:
        mapping = {
            "urls": self.urls_error,
            "destination": self.destination_error,
            "extra_arguments": self.extra_arguments_error,
        }
        for key, message in errors.items():
            if key in mapping:
                mapping[key].setText(message)
                mapping[key].setVisible(True)

    def _start_download(self) -> None:
        self._clear_errors()
        settings = self._collect_settings()
        urls = self._collect_urls()
        errors = validate_settings(settings, urls)
        try:
            shlex.split(settings.extra_arguments, posix=os.name != "nt")
        except ValueError:
            errors["extra_arguments"] = "Check quotation marks in extra arguments."
        if errors:
            self._show_errors(errors)
            self.status_label.setText("Review the highlighted fields.")
            return
        unique_urls, duplicates = find_duplicate_urls(urls)
        if duplicates:
            dialog = DuplicateUrlsDialog(duplicates, self)
            choice = dialog.exec()
            dialog.deleteLater()
            if choice == DuplicateUrlsDialog.SkipDuplicates:
                urls = unique_urls
                self._remove_duplicate_url_lines()
            elif choice != DuplicateUrlsDialog.DownloadAll:
                return
        destination = Path(settings.destination)
        try:
            destination.mkdir(parents=True, exist_ok=True)
            if not destination.is_dir():
                raise OSError("The destination is not a folder.")
        except OSError as error:
            self._show_errors({"destination": f"Cannot use this folder: {error}"})
            return
        try:
            self.settings_store.save(settings)
        except OSError as error:
            self._append_log(f"Could not save settings: {error}\n", "warning")
        self.downloaded = 0
        self.skipped = 0
        self.downloaded_bytes = 0
        self._counted_files.clear()
        self.tasks = [DownloadTask(url) for url in urls]
        self._active_task_index = None
        self._processed_tasks = 0
        self._batch_total = len(urls)
        self._run_started_at = time.monotonic()
        self._stopped_by_user = False
        self._update_mode = False
        self._active_settings = settings
        self.batch_counts.setText(f"{self._batch_total} URLs  •  0 files")
        self.transfer_stats.setText("0 B downloaded  •  0 B/s")
        self.progress.setRange(0, self._batch_total)
        self.progress.setValue(0)
        self.tasks_container.setVisible(True)
        self.task_list.clear()
        for _ in self.tasks:
            self.task_list.addItem(QListWidgetItem())
        self._refresh_tasks()
        self._start_next_task()

    def _start_next_task(self) -> None:
        try:
            index = next(i for i, task in enumerate(self.tasks) if task.status == "Pending")
        except StopIteration:
            self._active_task_index = None
            done = sum(task.status == "Done" for task in self.tasks)
            failed = sum(task.status == "Failed" for task in self.tasks)
            file_label = "file" if self.downloaded == 1 else "files"
            message = f"Download complete. {done} done, {failed} failed; {self.downloaded} {file_label} downloaded."
            self.status_label.setText(message)
            self._append_log(message + "\n", "error" if failed else "success")
            self._schedule_pending_close()
            return
        self._active_task_index = index
        self.tasks[index].status = "Downloading"
        self._refresh_tasks(index)
        assert self._active_settings is not None
        command = build_command(self._active_settings, [self.tasks[index].url])
        self._append_log(f"$ {shlex.join(command)}\n", "info")
        self.status_label.setText(f"Downloading URL {index + 1} of {self._batch_total}…")
        self.runner.start(command)

    def _refresh_tasks(self, changed_index: int | None = None) -> None:
        indexes = range(len(self.tasks)) if changed_index is None else (changed_index,)
        colors = {
            "Pending": ("#64748b", "#ffffff", "○"),
            "Downloading": ("#215b83", "#e8f3fb", "●"),
            "Done": ("#247255", "#eaf7ef", "✓"),
            "Failed": ("#b42318", "#fff0ee", "✕"),
            "Stopped": ("#9a6700", "#fff7e6", "■"),
        }
        for index in indexes:
            task = self.tasks[index]
            item = self.task_list.item(index)
            foreground, background, marker = colors[task.status]
            file_label = "file" if task.files == 1 else "files"
            item.setText(f"{marker}  {task.status}  •  {task.files} {file_label}  •  {task.url}")
            item.setToolTip(task.url)
            item.setForeground(QColor(foreground))
            item.setBackground(QColor(background))
            font = QFont(self.font())
            font.setBold(task.status == "Downloading")
            item.setFont(font)
        remaining = sum(task.status in {"Pending", "Downloading"} for task in self.tasks)
        done = sum(task.status == "Done" for task in self.tasks)
        failed = sum(task.status == "Failed" for task in self.tasks)
        self.task_summary.setText(f"{done} done  •  {remaining} remaining  •  {failed} failed")
        if self._active_task_index is not None:
            self.task_list.scrollToItem(self.task_list.item(self._active_task_index))

    def _stop_download(self) -> None:
        self._stopped_by_user = True
        self.status_label.setText("Stopping…")
        self.runner.stop()

    def _on_runner_state(self, state: str) -> None:
        running = state in {"running", "stopping"}
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(state == "running")
        self.update_button.setEnabled(not running)

    def _handle_output(self, text: str) -> None:
        combined = self._line_buffer + text
        lines = combined.splitlines(keepends=True)
        self._line_buffer = ""
        if lines and not lines[-1].endswith(("\n", "\r")):
            self._line_buffer = lines.pop()
        for line in lines:
            lowered = line.lower()
            kind = "normal"
            if "[error]" in lowered or "error:" in lowered:
                kind = "error"
            elif "[warning]" in lowered or "warning:" in lowered:
                kind = "warning"
            elif line.startswith("# "):
                self.skipped += 1
            elif not line.startswith("["):
                candidate = Path(line.strip().lstrip("✔ "))
                destination_text = self._active_settings.destination if self._active_settings else self._collect_settings().destination
                destination = Path(destination_text).expanduser()
                path = candidate if candidate.is_absolute() else destination / candidate
                try:
                    resolved = path.resolve()
                    if resolved.is_file() and resolved not in self._counted_files:
                        self._counted_files.add(resolved)
                        self.downloaded += 1
                        self.downloaded_bytes += resolved.stat().st_size
                        if self._active_task_index is not None:
                            self.tasks[self._active_task_index].files += 1
                            self._refresh_tasks(self._active_task_index)
                        kind = "success"
                except OSError:
                    pass
            self._append_log(line, kind)
        file_label = "file" if self.downloaded == 1 else "files"
        self.batch_counts.setText(f"{self._batch_total} URLs  •  {self.downloaded} {file_label}")
        elapsed = max(time.monotonic() - self._run_started_at, 1.0)
        self.transfer_stats.setText(f"{self._format_bytes(self.downloaded_bytes)} downloaded  •  {self._format_bytes(self.downloaded_bytes / elapsed)}/s")

    @staticmethod
    def _format_bytes(value: float) -> str:
        amount = max(0.0, float(value))
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if amount < 1000 or unit == "TB":
                return f"{amount:.0f} {unit}" if unit == "B" else f"{amount:.1f} {unit}"
            amount /= 1000
        return f"{amount:.1f} TB"

    def _append_log(self, text: str, kind: str = "normal") -> None:
        colors = {
            "normal": "#334155",
            "info": "#315b7c",
            "success": "#28745a",
            "warning": "#9a6700",
            "error": "#b42318",
        }
        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(colors.get(kind, colors["normal"])))
        cursor.insertText(text, fmt)
        self.log.setTextCursor(cursor)
        self.log.ensureCursorVisible()

    def _on_finished(self, exit_code: int) -> None:
        if self._line_buffer:
            pending = self._line_buffer + "\n"
            self._line_buffer = ""
            self._handle_output(pending)
        if self._update_mode:
            self._update_mode = False
            if exit_code == 0:
                self.status_label.setText("gallery-dl was updated successfully.")
                self._check_gallery_dl()
            else:
                self.status_label.setText(f"Update failed with exit code {exit_code}.")
            self._schedule_pending_close()
            return
        if self._active_task_index is None:
            self._schedule_pending_close()
            return
        index = self._active_task_index
        self.tasks[index].status = "Stopped" if self._stopped_by_user else ("Done" if exit_code == 0 else "Failed")
        self._active_task_index = None
        self._processed_tasks += 1
        self.progress.setValue(self._processed_tasks)
        self._refresh_tasks(index)
        if self._stopped_by_user:
            self.status_label.setText("Download stopped. Remaining URLs were not started.")
            self._append_log("Download stopped. Remaining URLs were not started.\n", "warning")
            self._schedule_pending_close()
        else:
            if exit_code != 0:
                self._append_log(f"URL {index + 1} failed with exit code {exit_code}.\n", "error")
            self._start_next_task()

    def _schedule_pending_close(self) -> None:
        if self._close_after_stop:
            self._close_after_stop = False
            QTimer.singleShot(0, self.close)

    def _check_gallery_dl(self) -> None:
        self.version_label.setText("Checking gallery-dl…")
        process = QProcess(self)
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        process.finished.connect(lambda code, status: self._version_checked(process, code))
        self._version_process = process
        command = gallery_dl_base_command() + ["--version"]
        process.start(command[0], command[1:])

    def _version_checked(self, process: QProcess, exit_code: int) -> None:
        version = bytes(process.readAllStandardOutput()).decode("utf-8", errors="replace").strip()
        if exit_code == 0 and version:
            self.version_label.setText(f"gallery-dl {version}")
        else:
            self.version_label.setText("gallery-dl is not installed")
        process.deleteLater()
        self._version_process = None

    def _update_gallery_dl(self) -> None:
        self._update_mode = True
        self._stopped_by_user = False
        self.status_label.setText("Updating gallery-dl…")
        self._append_log("Updating gallery-dl with pip…\n", "info")
        self.runner.start([sys.executable, "-m", "pip", "install", "-U", "gallery-dl"])

    def _paste_urls(self) -> None:
        text = QApplication.clipboard().text().strip()
        if not text:
            return
        current = self.urls_input.toPlainText().strip()
        self.urls_input.setPlainText(f"{current}\n{text}" if current else text)

    def _import_urls(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import URLs", "", "Text files (*.txt);;All files (*)")
        if path:
            try:
                text = Path(path).read_text(encoding="utf-8", errors="replace")
            except OSError as error:
                QMessageBox.warning(self, APP_NAME, f"Could not read the selected file: {error}")
                return
            current = self.urls_input.toPlainText().strip()
            self.urls_input.setPlainText(f"{current}\n{text}" if current else text)

    def _choose_destination(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose output folder", self.destination_input.text() or str(Path.home()))
        if path:
            self.destination_input.setText(path)

    def _open_destination(self) -> None:
        path = Path(self.destination_input.text()).expanduser()
        if path.is_dir():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _choose_cookie_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choose cookie file", "", "Text files (*.txt);;All files (*)")
        if path:
            self.cookie_file_input.setText(path)

    def _choose_config_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choose config file", "", "Config files (*.json *.conf *.yaml *.yml *.toml);;All files (*)")
        if path:
            self.config_file_input.setText(path)

    def closeEvent(self, event) -> None:
        if self.runner.is_running:
            choice = QMessageBox.question(self, APP_NAME, "A process is still running. Stop it and exit?")
            if choice != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self._close_after_stop = True
            self._stopped_by_user = True
            self.runner.stop()
            event.ignore()
            return
        try:
            self.settings_store.save(self._collect_settings())
        except OSError:
            pass
        event.accept()

    def _apply_style(self) -> None:
        from .resources import resource_path
        check_icon = str(resource_path("icons", "check.svg")).replace("\\", "/")
        dropdown_icon = str(resource_path("icons", "arrow_drop_down.svg")).replace("\\", "/")
        self.setStyleSheet("""
            QWidget#AppRoot { background: #f4f6f8; color: #1f2937; }
            QWidget { font-size: 13px; }
            QLabel#Brand { color: #183b56; }
            QLabel#Muted { color: #64748b; font-size: 12px; }
            QLabel#CardTitle, QLabel#SectionTitle { color: #183b56; font-size: 16px; font-weight: 500; }
            QLabel#Status { color: #334155; font-size: 15px; font-weight: 500; }
            QLabel#Pill { background: #e8eef3; color: #315b7c; border-radius: 11px; padding: 4px 10px; }
            QLabel#FieldError { color: #b42318; font-size: 11px; }
            QLabel#RequiredStar { color: #b42318; font-size: 16px; font-weight: 500; }
            QDialog#DuplicateUrlsDialog { background: #ffffff; border: 1px solid #dce3e9; }
            QLabel#DialogTitle { color: #183b56; font-size: 16px; font-weight: 500; }
            QFrame#DialogDivider { color: #dce3e9; }
            QFrame#Card, QFrame#ActivityPanel, QGroupBox {
                background: #ffffff; border: 1px solid #dce3e9; border-radius: 10px;
            }
            QFrame#ActivityPanel { border-radius: 12px; }
            QGroupBox { margin-top: 10px; padding: 12px 10px 10px 10px; font-weight: 500; color: #334155; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
            QLineEdit, QPlainTextEdit, QTextEdit, QComboBox {
                background: #ffffff; border: 1px solid #cbd5e1; border-radius: 7px; padding: 7px;
                selection-background-color: #8aa9bf;
            }
            QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #527b98; }
            QPushButton[adv_link=true] {
                background: transparent; border: none; color: #527b98;
                font-size: 12px; padding: 2px 0; text-align: left;
            }
            QPushButton[adv_link=true]:hover { color: #315b7c; text-decoration: underline; }
            QTextEdit#Log { background: #f8fafc; border-color: #d8e0e7; }

            QComboBox { padding-right: 28px; }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border-left: 1px solid #cbd5e1;
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
                background: #eef2f6;
            }
            QComboBox::drop-down:hover { background: #dde7ee; }
            QComboBox::down-arrow {
                image: url(""" + dropdown_icon + """);
                width: 14px; height: 14px; border: none;
            }
            QComboBox QAbstractItemView {
                background: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 7px;
                selection-background-color: #dde7ee;
                selection-color: #1f2937;
                padding: 4px;
                outline: 0;
            }
            QComboBox QAbstractItemView::item {
                min-height: 28px;
                padding: 4px 8px;
                border-radius: 5px;
            }

            QCheckBox { spacing: 8px; color: #334155; }
            QCheckBox::indicator {
                width: 16px; height: 16px;
                border: 1.5px solid #94a3b8;
                border-radius: 4px;
                background: #ffffff;
            }
            QCheckBox::indicator:hover { border-color: #527b98; background: #f0f6fb; }
            QCheckBox::indicator:checked {
                background: #315b7c;
                border-color: #315b7c;
                image: url(""" + check_icon + """);
            }
            QCheckBox::indicator:checked:hover { background: #274b67; border-color: #274b67; }

            QPushButton { background: #e8eef3; color: #243746; border: 1px solid #cbd8e1; border-radius: 7px; padding: 8px 12px; }
            QPushButton:hover { background: #dde7ee; }
            QPushButton:pressed { background: #d2dfe8; }
            QPushButton:disabled { color: #94a3b8; background: #edf1f4; }
            QPushButton#PrimaryButton { background: #315b7c; color: #ffffff; border-color: #315b7c; font-weight: 500; }
            QPushButton#PrimaryButton:hover { background: #274b67; }
            QPushButton#DialogCloseButton { background: transparent; color: #64748b; border: none; padding: 0; font-size: 20px; }
            QDialog#SettingsDialog { background: #f4f6f8; }
            QPushButton#DialogCloseButton:hover { background: #edf2f7; color: #183b56; }
            QPushButton[advanced="true"] { text-align: left; background: #ffffff; padding: 10px 12px; }
            QProgressBar { border: none; background: #dfe7ed; border-radius: 3px; min-height: 6px; max-height: 6px; }
            QProgressBar::chunk { background: #527b98; border-radius: 3px; }
            QListWidget#TaskList, QListWidget#DuplicateList { background: #ffffff; border: 1px solid #dce3e9; border-radius: 7px; outline: 0; }
            QListWidget#TaskList::item, QListWidget#DuplicateList::item { padding: 5px 7px; }
            QScrollArea { background: transparent; }
            QSplitter::handle { width: 12px; background: transparent; }

            QScrollBar:vertical {
                background: transparent; width: 6px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #c8d6e0; border-radius: 3px; min-height: 32px;
            }
            QScrollBar::handle:vertical:hover { background: #a0b8c8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
            QScrollBar:horizontal {
                background: transparent; height: 6px; margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: #c8d6e0; border-radius: 3px; min-width: 32px;
            }
            QScrollBar::handle:horizontal:hover { background: #a0b8c8; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
        """)
