<div align="center">

# IVA Downloader

**A modern desktop GUI for [gallery-dl](https://github.com/mikf/gallery-dl)**  
Download images and galleries from 300+ sites — with a clean interface, live output, and zero terminal work.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6%206.11-41CD52?style=flat-square&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![gallery-dl](https://img.shields.io/badge/gallery--dl-≥%201.32-FF6B6B?style=flat-square)](https://github.com/mikf/gallery-dl)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-5865F2?style=flat-square)](.)
[![Version](https://img.shields.io/badge/version-1.2.0-0ea5e9?style=flat-square)](pyproject.toml)

<br/>

<table>
  <tr>
    <td align="center"><strong>Main window</strong><br/><img src="docs/image_1.png" alt="IVA Downloader main window" width="520" /></td>
    <td align="center"><strong>Settings</strong><br/><img src="docs/image_2.png" alt="IVA Downloader settings with language, advanced options, and updates" width="520" /></td>
  </tr>
</table>

</div>

---

## Features

**Inputs**
- **Paste or type** URLs directly — one per line
- **Import from file** — load a `.txt` list of URLs in one click
- **Comment support** — lines starting with `#` are silently skipped
- **Duplicate warning** — remove repeated URL lines and download each link once, or confirm every occurrence
- **Cookie file** — point to a Netscape-format `cookies.txt` for sites requiring login

**Controls**
- **Custom destination** — pick any output folder, with a quick "open in explorer" button
- **Settings dialog** — choose English, Vietnamese, Japanese, or Chinese
- **Apply or cancel** — review settings changes before applying them
- **Update gallery-dl** — see the installed version and upgrade gallery-dl without leaving the app

**Activity panel**
- **Live log** — colour-coded output streams in real time (info, success, warning, error)
- **Task progress** — highlights the active URL, completed URLs, failures, and remaining count
- **Batch counter** — tracks URLs submitted and files downloaded
- **Stop anytime** — graceful terminate with a 3-second kill fallback
- **Transfer stats** — track downloaded files, total size, and average transfer speed

**UX**
- **Simple configuration** — gallery-dl options are edited directly in `gallery-dl.conf`
- **Polished light theme** — Qt Fusion palette with a custom stylesheet and SVG icons
- **Fixed two-panel layout** — setup on the left, activity on the right

---

## Getting started

> **Requires Python 3.10+.** Install [Python](https://www.python.org/downloads/) if you don't have it yet.

### Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./run.sh
```

### Windows — PowerShell / Command Prompt

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe gallery_dl_gui.py
```

## Quick guide

1. Open IVA Downloader using the launcher for your operating system.
2. Paste or type one gallery URL per line in the **URLs** box. Lines starting with `#` are treated as comments.
3. Choose a **Destination** folder for downloaded files. Add a cookies file only if the site requires you to sign in.
4. Select **Start download**. If URLs are repeated, choose **Skip duplicates** to download each URL once, or **Download duplicates** to download every occurrence.
5. Follow each URL's status in the **Activity** panel. Select **Stop** to halt the current batch.

Use **Settings** to choose the interface language, check for updates, or open the `gallery-dl.conf` configuration file by clicking its path. gallery-dl settings are stored in `gallery-dl.conf` and applied automatically. The file includes repost handling, artist-based filenames, and JSON metadata sidecars. Edit it directly to change those defaults. On Windows, the file is in `%APPDATA%\IVA Downloader`; on Linux, it is in `${XDG_CONFIG_HOME}/iva-downloader` or `~/.config/iva-downloader`. The GUI no longer saves a separate JSON preferences file.

### Supported languages

The **Language** selector in Settings offers:

- English
- Tiếng Việt (Vietnamese)
- 日本語 (Japanese)
- 中文 (Chinese, Simplified)

## Dependencies

| Package | Version | Role |
|---|---|---|
| [gallery-dl](https://github.com/mikf/gallery-dl) | ≥ 1.32 | Download engine |
| [PySide6](https://doc.qt.io/qtforpython/) | 6.11.x | Qt GUI bindings |

Dev only: `pytest ≥ 9`, `pytest-qt ≥ 4.5`
