"""Native library discovery and runtime loading for bundled JME binaries."""

from __future__ import annotations

import os
import platform
from ctypes import CDLL, RTLD_GLOBAL
from pathlib import Path


class JmeLibraryNotFoundError(RuntimeError):
    """Raised when no compatible JME shared library is found."""


def _normalized_arch() -> str:
    arch = platform.machine().lower()
    if arch in {"x86_64", "amd64"}:
        return "x64"
    if arch in {"aarch64", "arm64"}:
        return "arm64"
    return arch


def _platform_dir() -> str:
    system = platform.system()
    arch = _normalized_arch()
    if system == "Windows":
        return f"windows-{arch}"
    if system == "Darwin":
        return f"macos-{arch}"
    return f"linux-{arch}"


def _filename(kind: str) -> str:
    system = platform.system()
    if kind == "jme":
        if system == "Windows":
            return "jme.dll"
        if system == "Darwin":
            return "libjme.dylib"
        return "libjme.so"
    if system == "Windows":
        return "calceph.dll"
    if system == "Darwin":
        return "libcalceph.dylib"
    return "libcalceph.so"


def _candidate_paths(filename: str) -> list[Path]:
    package_root = Path(__file__).resolve().parent
    platform_dir = _platform_dir()
    candidates = [package_root / "libs" / platform_dir / filename]

    system = platform.system()
    if system in {"Linux", "Darwin"}:
        candidates.extend(
            [
                Path("/usr/local/lib") / filename,
                Path("/usr/lib") / filename,
                Path("/lib/x86_64-linux-gnu") / filename,
                Path("/lib/aarch64-linux-gnu") / filename,
            ]
        )

    return candidates


def _find_path(env_var: str, kind: str) -> Path:
    env_path = os.environ.get(env_var)
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        raise JmeLibraryNotFoundError(f"{env_var} does not exist: {path}")

    filename = _filename(kind)
    candidates = _candidate_paths(filename)
    for candidate in candidates:
        if candidate.exists():
            return candidate

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise JmeLibraryNotFoundError(f"{kind.upper()} library not found. Searched: {searched}")


def find_library() -> Path:
    """Find the platform-appropriate JME shared library."""

    return _find_path("JME_LIBRARY_PATH", "jme")


def find_calceph_library() -> Path:
    """Find the platform-appropriate CALCEPH shared library."""

    return _find_path("JME_CALCEPH_LIBRARY_PATH", "calceph")


def load_calceph_runtime() -> CDLL | None:
    """Best-effort preload of CALCEPH so JME can resolve kernel-mode symbols."""

    try:
        path = find_calceph_library()
    except JmeLibraryNotFoundError:
        return None

    if platform.system() == "Windows":
        return CDLL(str(path))
    return CDLL(str(path), mode=RTLD_GLOBAL)


__all__ = [
    "JmeLibraryNotFoundError",
    "find_calceph_library",
    "find_library",
    "load_calceph_runtime",
]
