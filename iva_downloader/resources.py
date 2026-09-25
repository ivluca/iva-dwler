from pathlib import Path

from PySide6.QtGui import QFontDatabase, QIcon


ICON_NAMES = (
    "download",
    "stop_circle",
    "content_paste",
    "file_open",
    "delete_sweep",
    "folder_open",
    "open_in_new",
    "tune",
    "system_update_alt",
    "cookie",
    "download_for_offline",
)


def resource_path(*parts: str) -> Path:
    return Path(__file__).resolve().parent / "assets" / Path(*parts)


def load_app_font() -> str:
    font_id = QFontDatabase.addApplicationFont(str(resource_path("fonts", "SNPro-Variable.ttf")))
    if font_id < 0:
        return ""
    families = QFontDatabase.applicationFontFamilies(font_id)
    return families[0] if families else ""


def icon(name: str) -> QIcon:
    return QIcon(str(resource_path("icons", f"{name}.svg")))
