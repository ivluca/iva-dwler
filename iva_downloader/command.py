import shlex
import sys

from .models import DownloadSettings


def gallery_dl_base_command() -> list[str]:
    return [sys.executable, "-m", "gallery_dl"]


def split_extra_arguments(value: str) -> list[str]:
    return shlex.split(value, posix=True)


def build_command(settings: DownloadSettings, urls: list[str]) -> list[str]:
    command = gallery_dl_base_command()
    destination = settings.destination.strip()
    for flag, value in (("-d", destination), ("-c", settings.config_file.strip())):
        if value:
            command.extend([flag, value])

    if settings.cookie_file.strip():
        command.extend(["--cookies", settings.cookie_file.strip()])

    if settings.simulate:
        command.append("--simulate")
    if settings.verbose:
        command.append("-v")
    if settings.extra_arguments.strip():
        command.extend(split_extra_arguments(settings.extra_arguments))
    return command + list(urls)
