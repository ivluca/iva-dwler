from iva_downloader.models import DownloadSettings, find_duplicate_urls, validate_settings


def test_validate_settings_rejects_missing_urls_and_destination():
    errors = validate_settings(DownloadSettings(destination=""), [])

    assert errors == {
        "urls": "Add at least one URL.",
        "destination": "Choose an output folder.",
    }


def test_validate_settings_rejects_invalid_jobs():
    settings = DownloadSettings(destination="downloads", jobs="0")

    errors = validate_settings(settings, ["https://example.com/gallery"])

    assert "jobs" in errors


def test_validate_settings_rejects_non_integer_jobs():
    settings = DownloadSettings(destination="downloads", jobs="abc")

    errors = validate_settings(settings, ["https://example.com/gallery"])

    assert "jobs" in errors


def test_validate_settings_accepts_valid_jobs():
    settings = DownloadSettings(destination="downloads", jobs="4")

    errors = validate_settings(settings, ["https://example.com/gallery"])

    assert "jobs" not in errors


def test_validate_settings_accepts_blank_jobs():
    settings = DownloadSettings(destination="downloads", jobs="")

    errors = validate_settings(settings, ["https://example.com/gallery"])

    assert "jobs" not in errors


def test_find_duplicate_urls_keeps_first_occurrences_and_reports_counts():
    unique, duplicates = find_duplicate_urls(["a", "b", "a", "c", "b", "a"])

    assert unique == ["a", "b", "c"]
    assert duplicates == [("a", 3), ("b", 2)]
