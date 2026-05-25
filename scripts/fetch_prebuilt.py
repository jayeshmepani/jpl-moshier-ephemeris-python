"""Install bundled JME and CALCEPH runtimes from the PHP wrapper source."""

from __future__ import annotations

import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


def default_local_source() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "jpl-moshier-ephemeris-php"
        / "libs"
    )


def archive_url() -> str:
    repo = os.environ.get("JME_PHP_REPO", "jayeshmepani/jpl-moshier-ephemeris-php")
    tag = os.environ.get("JME_PHP_TAG", "prebuilt-libs")
    return os.environ.get(
        "JME_PHP_ARCHIVE_URL",
        f"https://github.com/{repo}/archive/refs/tags/{tag}.zip",
    )


def install_from_directory(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def install_from_archive(destination: Path) -> None:
    tmp_root = Path(tempfile.gettempdir()) / "jme-python-prebuilt"
    tmp_root.mkdir(parents=True, exist_ok=True)
    archive_path = tmp_root / "jpl-moshier-ephemeris-php-prebuilt.zip"
    urllib.request.urlretrieve(archive_url(), archive_path)

    extract_root = tmp_root / "extract"
    if extract_root.exists():
        shutil.rmtree(extract_root)
    extract_root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive_path) as zf:
        zf.extractall(extract_root)

    libs_dir = next(extract_root.glob("jpl-moshier-ephemeris-php-*/libs"), None)
    if libs_dir is None:
        raise SystemExit("Downloaded archive does not contain a libs directory.")

    install_from_directory(libs_dir, destination)


def validate(destination: Path) -> None:
    required = {
        "linux-x64/libjme.so",
        "linux-x64/libcalceph.so",
        "linux-arm64/libjme.so",
        "linux-arm64/libcalceph.so",
        "macos-x64/libjme.dylib",
        "macos-x64/libcalceph.dylib",
        "macos-arm64/libjme.dylib",
        "macos-arm64/libcalceph.dylib",
        "windows-x64/jme.dll",
        "windows-x64/calceph.dll",
    }
    missing = [item for item in sorted(required) if not (destination / item).exists()]
    if missing:
        raise SystemExit(f"Missing expected runtime files: {', '.join(missing)}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    destination = root / "src" / "jpl_moshier_ephemeris" / "libs"
    override = os.environ.get("JME_PHP_LIBS_PATH")
    source = Path(override).expanduser() if override else default_local_source()

    if source.exists():
        print(f"Copying runtimes from local source: {source}")
        install_from_directory(source, destination)
    else:
        print(f"Local runtime source not found at {source}")
        print(f"Downloading runtimes from {archive_url()}")
        install_from_archive(destination)

    validate(destination)
    print(f"Installed runtimes into {destination}")


if __name__ == "__main__":
    main()
