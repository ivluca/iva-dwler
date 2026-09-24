import sys

from iva_downloader.command import build_command, split_extra_arguments
from iva_downloader.models import DownloadSettings


def test_build_command_maps_curated_settings_to_gallery_dl_flags(tmp_path):
    destination = tmp_path / "downloads"
    settings = DownloadSettings(
        destination=str(destination),
        cookie_file="cookies.txt",
        config_file="gallery-dl.conf",
        simulate=True,
        verbose=True,
        extra_arguments='--user-agent "IVA Downloader"',
    )

    cmd = build_command(settings, ["https://example.com/a", "https://example.com/b"])

    assert cmd[:3] == [sys.executable, "-m", "gallery_dl"]
    assert "-d" in cmd
    assert "-c" in cmd
    assert "--cookies" in cmd
    assert "--simulate" in cmd
    assert "-v" in cmd
    assert "--user-agent" in cmd
    assert "https://example.com/a" in cmd
    assert "https://example.com/b" in cmd


def test_build_command_never_emits_browser_cookie_flag():
    settings = DownloadSettings(destination="downloads")

    built = build_command(settings, ["https://example.com/gallery"])

    assert "--cookies-from-browser" not in built
    assert "--cookies" not in built


def test_split_extra_arguments_handles_quoted_strings():
    value = '--user-agent "IVA Downloader" --retries 3'

    assert split_extra_arguments(value) == [
        "--user-agent",
        "IVA Downloader",
        "--retries",
        "3",
    ]
