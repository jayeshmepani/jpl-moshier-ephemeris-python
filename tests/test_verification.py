from __future__ import annotations

import os
import re
from pathlib import Path

import jpl_moshier_ephemeris as jme_pkg
import pytest


def _native_root() -> Path | None:
    env_path = os.environ.get("JME_SOURCE_PATH")
    if env_path:
        path = Path(env_path)
        return path if path.exists() else None

    candidates = [
        Path(__file__).resolve().parents[3] / "jpl-ephemeris-",
        Path(__file__).resolve().parents[3] / "jpl-ephemeris",
        Path("/home/shreesoftech/projects/test1/astro_packages/jpl-ephemeris-"),
    ]
    return next((candidate for candidate in candidates if candidate.exists()), None)


@pytest.fixture
def native_root() -> Path:
    root = _native_root()
    if root is None:
        pytest.skip("native jpl-ephemeris- tree not available")
    return root


def test_generated_constants_count() -> None:
    constants = [name for name in vars(jme_pkg) if name.startswith("JME_")]
    assert len(constants) == 462


def test_surface_matches_native_inventory(native_root: Path) -> None:
    api_reference = (native_root / "docs" / "API_REFERENCE.md").read_text()
    tracked_functions = sorted(
        set(re.findall(r"\|\s*\d+\s*\|\s*`(jme_[A-Za-z0-9_]+)`\s*\|", api_reference))
    )
    assert len(tracked_functions) == 204
    assert sorted(jme_pkg.signature_names()) == tracked_functions

    headers = (
        (native_root / "include" / "jme" / "jme.h").read_text()
        + "\n"
        + (native_root / "include" / "jme" / "jme_extended.h").read_text()
    )
    native_constants = sorted(set(re.findall(r"\b(JME_[A-Z0-9_]+)\b", headers)))
    python_constants = sorted(name for name in vars(jme_pkg) if name.startswith("JME_"))

    assert len(native_constants) == 462
    assert python_constants == native_constants
