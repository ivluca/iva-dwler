from pathlib import Path

from .models import DownloadSettings


class SettingsStore:
    def __init__(self, path: Path | None = None):
        # Kept as an injectable in-memory store; user preferences are no longer
        # serialized to a separate JSON file.
        self.path = path
        self._settings = DownloadSettings()

    def load(self) -> DownloadSettings:
        return DownloadSettings(**vars(self._settings))

    def save(self, settings: DownloadSettings) -> None:
        self._settings = DownloadSettings(**vars(settings))
