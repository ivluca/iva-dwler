import os
from pathlib import Path
import shutil


def default_gallery_dl_config_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "IVA Downloader" / "gallery-dl.conf"
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "iva-downloader" / "gallery-dl.conf"


class GalleryDLConfigStore:
    def __init__(self, path: Path | None = None):
        self.path = path or default_gallery_dl_config_path()
        self.template_path = Path(__file__).resolve().parent / "assets" / "gallery-dl.conf"

    def ensure_exists(self) -> Path:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.template_path, self.path)
        return self.path
