import os
import shutil
import subprocess
from pathlib import Path

import pytest
from swisseph_ffi import SEFLG_SPEED, SEFLG_SWIEPH, SwissEph, c_double, create_string_buffer


def _find_swetest() -> Path | None:
    env_path = os.environ.get("SWETEST_PATH")
    if env_path:
        path = Path(env_path)
        return path if path.exists() else None

    exe = "swetest.exe" if os.name == "nt" else "swetest"
    found = shutil.which(exe)
    if found:
        return Path(found)

    sibling = Path(__file__).resolve().parents[2] / "Swiss-Ephemeris-PHP"
    candidates = [
        sibling / "build" / "swisseph_src" / "bin" / exe,
        sibling / ".github" / "build" / "swisseph_src" / "bin" / exe,
        sibling / ".github" / "build" / "swisseph_src" / "windows" / "programs" / exe,
    ]
    return next((candidate for candidate in candidates if candidate.exists()), None)


def _find_ephe_path() -> Path | None:
    env_path = os.environ.get("SWISSEPH_EPHE_PATH")
    if env_path:
        path = Path(env_path)
        return path if path.exists() else None

    sibling = Path(__file__).resolve().parents[2] / "Swiss-Ephemeris-PHP"
    candidates = [
        sibling / "build" / "swisseph_src" / "ephe",
        sibling / ".github" / "build" / "swisseph_src" / "ephe",
    ]
    return next((candidate for candidate in candidates if candidate.exists()), None)


@pytest.fixture
def swetest_context() -> tuple[Path, Path]:
    swetest = _find_swetest()
    ephe_path = _find_ephe_path()
    if swetest is None or ephe_path is None:
        pytest.skip("swetest CLI or ephemeris path not available")
    return swetest, ephe_path


@pytest.mark.parametrize(
    ("jd", "ipl"),
    [
        (2451545.0, 0),
        (2461155.5, 1),
    ],
)
def test_planet_parity(swetest_context: tuple[Path, Path], jd: float, ipl: int) -> None:
    swetest, ephe_path = swetest_context
    expected = float(
        subprocess.check_output(
            [str(swetest), f"-p{ipl}", f"-bj{jd}", "-fl", "-head", f"-edir{ephe_path}"],
            text=True,
        ).strip()
    )

    swe = SwissEph()
    swe.swe_set_ephe_path(str(ephe_path).encode())
    xx = (c_double * 6)()
    serr = create_string_buffer(256)
    swe.swe_calc(jd, ipl, SEFLG_SPEED | SEFLG_SWIEPH, xx, serr)

    assert xx[0] == pytest.approx(expected, abs=0.00001)


def test_house_parity(swetest_context: tuple[Path, Path]) -> None:
    swetest, ephe_path = swetest_context
    jd = 2451545.0
    lat = 51.5074
    lon = -0.1278
    output = subprocess.check_output(
        [
            str(swetest),
            f"-bj{jd}",
            f"-geopos{lon},{lat},0",
            "-house",
            "-fl",
            "-head",
            "-ut",
            f"-edir{ephe_path}",
        ],
        text=True,
    )
    expected_cusp_1 = float(output.strip().splitlines()[13])

    swe = SwissEph()
    swe.swe_set_ephe_path(str(ephe_path).encode())
    cusps = (c_double * 13)()
    ascmc = (c_double * 10)()
    swe.swe_houses(jd, lat, lon, ord("P"), cusps, ascmc)

    assert expected_cusp_1 > 0
    assert cusps[1] == pytest.approx(expected_cusp_1, abs=0.0001)


def test_eclipse_parity(swetest_context: tuple[Path, Path]) -> None:
    swetest, ephe_path = swetest_context
    jd_start = 2460000.5
    swe = SwissEph()
    swe.swe_set_ephe_path(str(ephe_path).encode())
    tret = (c_double * 10)()
    serr = create_string_buffer(256)
    swe.swe_lun_eclipse_when(jd_start, SEFLG_SWIEPH, 0, tret, 0, serr)

    output = subprocess.check_output(
        [str(swetest), f"-bj{jd_start}", "-lunecl", "-head", f"-edir{ephe_path}"],
        text=True,
    )

    assert f"{tret[0]:.4f}" in output
