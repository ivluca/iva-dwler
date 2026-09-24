import json

from iva_downloader.models import DownloadSettings
from iva_downloader.settings import SettingsStore


def test_settings_store_migrates_legacy_keys(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({
        "dest": "/legacy/output",
        "cookies": "/legacy/cookies.txt",
        "config": "/legacy/config.json",
        "simulate": True,
        "verbose": True,
        "extra": "--no-mtime",
    }), encoding="utf-8")

    settings = SettingsStore(path).load()

    assert settings.destination == "/legacy/output"
    assert settings.cookie_file == "/legacy/cookies.txt"
    assert settings.config_file == "/legacy/config.json"
    assert settings.simulate is True
    assert settings.verbose is True
    assert settings.extra_arguments == "--no-mtime"


def test_settings_store_round_trips_all_fields(tmp_path):
    path = tmp_path / "settings.json"
    original = DownloadSettings(
        destination="downloads",
        cookie_file="cookies.txt",
        config_file="gallery-dl.conf",
        jobs="4",
        simulate=False,
        verbose=True,
        extra_arguments="--no-mtime",
    )

    store = SettingsStore(path)
    store.save(original)

    assert store.load() == original


def test_settings_store_returns_defaults_for_invalid_json(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("not-json", encoding="utf-8")

    assert SettingsStore(path).load() == DownloadSettings()


def test_settings_store_ignores_wrong_field_types_without_crashing(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({
        "cookies": 42,
        "jobs": True,
        "simulate": "yes",
    }), encoding="utf-8")

    settings = SettingsStore(path).load()

    assert settings.cookie_file == ""
    assert settings.jobs == ""
    assert settings.simulate is False
