"""Fetch all prebuilt Swiss Ephemeris binaries from the PHP sibling release."""

from __future__ import annotations

import os
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ASSETS = {
    "linux-x64": ("libswe.so", "libswe-linux-x64.tar.gz"),
    "linux-arm64": ("libswe.so", "libswe-linux-arm64.tar.gz"),
    "macos-x64": ("libswe.dylib", "libswe-macos-x64.tar.gz"),
    "macos-arm64": ("libswe.dylib", "libswe-macos-arm64.tar.gz"),
    "windows-x64": ("swe.dll", "libswe-windows-x64.zip"),
}


def extract(asset_path: Path, out_dir: Path) -> None:
    if asset_path.suffix == ".zip":
        with zipfile.ZipFile(asset_path) as zf:
            zf.extractall(out_dir)
        return
    with tarfile.open(asset_path, "r:gz") as tf:
        tf.extractall(out_dir)


def main() -> None:
    repo = os.environ.get("SWISSEPH_LIBS_REPO", "jayeshmepani/Swiss-Ephemeris-PHP")
    release = os.environ.get("SWISSEPH_LIBS_RELEASE", "v1.1.0")
    base = os.environ.get(
        "SWISSEPH_LIBS_BASE_URL", f"https://github.com/{repo}/releases/download/{release}"
    )
    root = Path(__file__).resolve().parents[1]
    libs_root = root / "src" / "swisseph_ffi" / "libs"
    tmp_dir = Path(tempfile.gettempdir()) / "swisseph-ffi-libs"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for platform_dir, (filename, asset) in ASSETS.items():
        out_dir = libs_root / platform_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        url = f"{base.rstrip('/')}/{asset}"
        asset_path = tmp_dir / asset
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, asset_path)
        extract(asset_path, out_dir)
        expected = out_dir / filename
        if not expected.exists():
            raise SystemExit(f"Downloaded archive did not contain expected file: {expected}")
        print(f"Installed {expected}")


if __name__ == "__main__":
    main()
