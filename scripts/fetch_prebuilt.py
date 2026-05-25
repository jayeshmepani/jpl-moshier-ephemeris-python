"""Install bundled JME and CALCEPH runtimes from the PHP wrapper source."""

from __future__ import annotations

import os
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ASSETS = {
    "linux-x64": "jme-linux-x64.tar.gz",
    "linux-arm64": "jme-linux-arm64.tar.gz",
    "macos-x64": "jme-macos-x64.tar.gz",
    "macos-arm64": "jme-macos-arm64.tar.gz",
    "windows-x64": "jme-windows-x64.zip",
}


def default_local_source() -> Path:
    return Path(__file__).resolve().parents[2] / "jpl-moshier-ephemeris-php" / "libs"


def release_base_url() -> str:
    repo = os.environ.get("JME_PHP_REPO", "jayeshmepani/jpl-moshier-ephemeris-php")
    tag = os.environ.get("JME_PHP_TAG", "prebuilt-libs")
    return os.environ.get(
        "JME_PHP_RELEASE_BASE_URL",
        f"https://github.com/{repo}/releases/download/{tag}",
    )


def install_from_directory(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def extract_archive(archive_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(out_dir)
        return
    with tarfile.open(archive_path, "r:gz") as tf:
        tf.extractall(out_dir)


def install_from_release_assets(destination: Path) -> None:
    tmp_root = Path(tempfile.gettempdir()) / "jme-python-prebuilt"
    tmp_root.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    base_url = release_base_url().rstrip("/")

    for platform_dir, asset_name in ASSETS.items():
        url = f"{base_url}/{asset_name}"
        archive_path = tmp_root / asset_name
        out_dir = destination / platform_dir
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, archive_path)
        extract_archive(archive_path, out_dir)


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
        print(f"Downloading runtimes from {release_base_url()}")
        install_from_release_assets(destination)

    validate(destination)
    print(f"Installed runtimes into {destination}")


if __name__ == "__main__":
    main()
