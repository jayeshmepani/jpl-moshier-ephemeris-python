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
    "jme-linux-x64-ubuntu24": "jme-linux-x64-ubuntu24.tar.gz",
    "jme-linux-arm64-ubuntu24": "jme-linux-arm64-ubuntu24.tar.gz",
    "jme-linux-x64-ubuntu22": "jme-linux-x64-ubuntu22.tar.gz",
    "jme-linux-arm64-ubuntu22": "jme-linux-arm64-ubuntu22.tar.gz",
    "jme-macos-x64-15": "jme-macos-x64-15.tar.gz",
    "jme-macos-arm64-15": "jme-macos-arm64-15.tar.gz",
    "jme-macos-arm64-14": "jme-macos-arm64-14.tar.gz",
    "jme-windows-x64-2022": "jme-windows-x64-2022.zip",
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
        "jme-linux-x64-ubuntu24/libjme.so",
        "jme-linux-x64-ubuntu24/libcalceph.so",
        "jme-linux-arm64-ubuntu24/libjme.so",
        "jme-linux-arm64-ubuntu24/libcalceph.so",
        "jme-linux-x64-ubuntu22/libjme.so",
        "jme-linux-x64-ubuntu22/libcalceph.so",
        "jme-linux-arm64-ubuntu22/libjme.so",
        "jme-linux-arm64-ubuntu22/libcalceph.so",
        "jme-macos-x64-15/libjme.dylib",
        "jme-macos-x64-15/libcalceph.dylib",
        "jme-macos-arm64-15/libjme.dylib",
        "jme-macos-arm64-15/libcalceph.dylib",
        "jme-macos-arm64-14/libjme.dylib",
        "jme-macos-arm64-14/libcalceph.dylib",
        "jme-windows-x64-2022/jme.dll",
        "jme-windows-x64-2022/calceph.dll",
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
