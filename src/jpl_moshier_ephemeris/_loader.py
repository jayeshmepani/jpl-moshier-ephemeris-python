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
    package_root = Path(__file__).resolve().parent
    libs_dir = package_root / "libs"

    if system == "Windows":
        return "jme-windows-x64-2022"

    if system == "Darwin":
        if arch == "arm64":
            mac_ver = platform.mac_ver()[0]
            try:
                major = int(mac_ver.split(".")[0])
            except (ValueError, IndexError):
                major = 15  # Default to latest if check fails

            dir_name = f"jme-macos-arm64-{15 if major >= 15 else 14}"
            if not (libs_dir / dir_name).exists():
                return f"jme-macos-arm64-{14 if major >= 15 else 15}"
            return dir_name
        return "jme-macos-x64-15"

    # Linux / other Unix
    libc_name, libc_version = platform.libc_ver()
    glibc_ver = None
    if libc_name == "glibc" and libc_version:
        try:
            parts = [int(p) for p in libc_version.split(".")]
            if len(parts) >= 2:
                glibc_ver = parts[:2]
        except ValueError:
            pass

    # Fallback to os-release parsing if glibc version not detected
    if glibc_ver is None and Path("/etc/os-release").exists():
        try:
            os_release = {}
            with open("/etc/os-release") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        os_release[k] = v.strip('"')
            id_ = os_release.get("ID", "").lower()
            version_id = os_release.get("VERSION_ID", "")
            if id_ == "ubuntu" or "ubuntu" in os_release.get("ID_LIKE", "").lower():
                try:
                    if float(version_id) >= 24.0:
                        glibc_ver = [2, 39]
                except ValueError:
                    pass
            elif id_ == "debian":
                try:
                    if float(version_id) >= 13.0:
                        glibc_ver = [2, 39]
                except ValueError:
                    pass
        except Exception:
            pass

    suffix = "ubuntu24" if glibc_ver and glibc_ver >= [2, 39] else "ubuntu22"
    dir_name = f"jme-linux-{arch}-{suffix}"
    if not (libs_dir / dir_name).exists():
        fallback_suffix = "ubuntu22" if suffix == "ubuntu24" else "ubuntu24"
        return f"jme-linux-{arch}-{fallback_suffix}"
    return dir_name


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
