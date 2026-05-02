"""Native library discovery for bundled Swiss Ephemeris binaries."""

from __future__ import annotations

import os
import platform
from pathlib import Path


class SwissEphLibraryNotFoundError(RuntimeError):
    """Raised when no compatible Swiss Ephemeris shared library is found."""


def _normalized_arch() -> str:
    arch = platform.machine().lower()
    if arch in {"x86_64", "amd64"}:
        return "x64"
    if arch in {"aarch64", "arm64"}:
        return "arm64"
    return arch


def _platform_dir_and_file() -> tuple[str, str]:
    system = platform.system()
    arch = _normalized_arch()
    if system == "Windows":
        return f"windows-{arch}", "swe.dll"
    if system == "Darwin":
        return f"macos-{arch}", "libswe.dylib"
    return f"linux-{arch}", "libswe.so"


def find_library() -> Path:
    """Find the native Swiss Ephemeris library for the current platform.

    Search order:
    1. ``SWISSEPH_LIBRARY_PATH``
    2. bundled package binary under ``libs/<os-arch>/``
    3. common system library locations on Linux/macOS
    """

    env_path = os.environ.get("SWISSEPH_LIBRARY_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        raise SwissEphLibraryNotFoundError(f"SWISSEPH_LIBRARY_PATH does not exist: {path}")

    platform_dir, filename = _platform_dir_and_file()
    package_root = Path(__file__).resolve().parent
    candidates = [package_root / "libs" / platform_dir / filename]

    system = platform.system()
    if system in {"Linux", "Darwin"}:
        candidates.extend(
            [
                Path("/usr/local/lib") / filename,
                Path("/usr/lib") / filename,
            ]
        )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise SwissEphLibraryNotFoundError(f"Swiss Ephemeris library not found. Searched: {searched}")


__all__ = ["SwissEphLibraryNotFoundError", "find_library"]
