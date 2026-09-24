from dataclasses import dataclass
import re


@dataclass
class DownloadSettings:
    destination: str = ""
    cookie_file: str = ""
    config_file: str = ""
    jobs: str = ""
    simulate: bool = False
    verbose: bool = False
    extra_arguments: str = ""


def validate_settings(settings: DownloadSettings, urls: list[str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not urls:
        errors["urls"] = "Add at least one URL."
    if not settings.destination.strip():
        errors["destination"] = "Choose an output folder."

    jobs = settings.jobs.strip()
    if jobs:
        try:
            if int(jobs) < 1:
                raise ValueError
        except ValueError:
            errors["jobs"] = "Enter a whole number ≥ 1."

    return errors
