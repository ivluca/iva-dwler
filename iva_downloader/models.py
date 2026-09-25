from dataclasses import dataclass
from collections import Counter
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
    language: str = "en"


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


def find_duplicate_urls(urls: list[str]) -> tuple[list[str], list[tuple[str, int]]]:
    """Keep each URL's first occurrence and list repeated URLs in input order."""
    counts = Counter(urls)
    unique = list(dict.fromkeys(urls))
    duplicates = [(url, counts[url]) for url in unique if counts[url] > 1]
    return unique, duplicates
