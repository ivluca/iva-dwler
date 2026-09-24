from dataclasses import asdict, fields
import json
from pathlib import Path

from .models import DownloadSettings


class SettingsStore:
    LEGACY_KEYS = {
        "dest": "destination",
        "cookies": "cookie_file",
        "config": "config_file",
        "extra": "extra_arguments",
    }

    def __init__(self, path: Path | None = None):
        self.path = path or Path.home() / ".gallery_dl_gui.json"

    def load(self) -> DownloadSettings:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return DownloadSettings()
        if not isinstance(data, dict):
            return DownloadSettings()

        normalized = dict(data)
        for old_key, new_key in self.LEGACY_KEYS.items():
            if new_key not in normalized and old_key in normalized:
                normalized[new_key] = normalized[old_key]
        defaults = DownloadSettings()
        known = {field.name for field in fields(DownloadSettings)}
        values = {
            key: value
            for key, value in normalized.items()
            if key in known and type(value) is type(getattr(defaults, key))
        }
        return DownloadSettings(**values)

    def save(self, settings: DownloadSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(asdict(settings), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
