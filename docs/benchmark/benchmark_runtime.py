"""Runtime benchmark for Python Swiss Ephemeris bindings.

Run this script from separate virtual environments because ``pyswisseph`` and
``pysweph`` both expose the same import name: ``swisseph``.
"""

from __future__ import annotations

import argparse
import gc
import importlib.metadata
import json
import os
import platform
import statistics
import sys
import time
from collections.abc import Callable
from ctypes import c_char, c_char_p, c_double, c_int, create_string_buffer
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class BenchResult:
    name: str
    iterations: int
    warmup: int
    repeats: int
    mean_ns: float
    median_ns: float
    min_ns: float
    max_ns: float


def measure(
    name: str,
    fn: Callable[[], object],
    iterations: int,
    warmup: int,
    repeats: int,
) -> BenchResult:
    samples: list[float] = []
    for _ in range(repeats):
        for _ in range(warmup):
            fn()
        gc.disable()
        try:
            start = time.perf_counter_ns()
            for _ in range(iterations):
                fn()
            elapsed = time.perf_counter_ns() - start
        finally:
            gc.enable()
        samples.append(elapsed / iterations)
    return BenchResult(
        name=name,
        iterations=iterations,
        warmup=warmup,
        repeats=repeats,
        mean_ns=statistics.mean(samples),
        median_ns=statistics.median(samples),
        min_ns=min(samples),
        max_ns=max(samples),
    )


def package_version(distribution: str) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def system_metadata(library: str, distribution: str) -> dict[str, object]:
    memory_bytes = None
    if hasattr(os, "sysconf"):
        try:
            memory_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        except (OSError, ValueError):
            memory_bytes = None
    if memory_bytes is None and platform.system() == "Windows":
        try:
            import ctypes

            class MemoryStatus(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            status = MemoryStatus()
            status.dwLength = ctypes.sizeof(status)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
            memory_bytes = int(status.ullTotalPhys)
        except (AttributeError, OSError):
            memory_bytes = None

    return {
        "library": library,
        "distribution": distribution,
        "distribution_version": package_version(distribution),
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "python_version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "compiler": platform.python_compiler(),
        "os": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "ram_bytes": memory_bytes,
    }


def ffi_cases() -> tuple[dict[str, Callable[[], object]], dict[str, object]]:
    import swisseph_ffi as swec
    from swisseph_ffi import SwissEph
    from swisseph_ffi.bindings import _SIGNATURES

    swe = SwissEph()
    jd = swe.swe_julday(2026, 5, 2, 12.0, swec.SE_GREG_CAL)
    flags = swec.SEFLG_SWIEPH | swec.SEFLG_SPEED
    xx = (c_double * 6)()
    xpo = (c_double * 3)(72.5714, 23.0225, 0.0)
    xaz = (c_double * 3)()
    cusps = (c_double * 13)()
    ascmc = (c_double * 10)()
    serr = create_string_buffer(256)
    dret = (c_double * 10)()
    utc_dret = (c_double * 2)()
    rev_year = c_int()
    rev_month = c_int()
    rev_day = c_int()
    rev_hour = c_double()
    split_deg = c_int()
    split_min = c_int()
    split_sec = c_int()
    split_frac = c_double()
    split_sign = c_int()

    metadata = system_metadata("swisseph-ffi", "swisseph-ffi")
    metadata["native_library"] = str(swe.library_path)
    metadata["swiss_ephemeris_version"] = None
    version_buffer = create_string_buffer(256)
    swe.swe_version(version_buffer)
    metadata["swiss_ephemeris_version"] = version_buffer.value.decode(errors="replace")

    curated_cases = {
        "julday": lambda: swe.swe_julday(2026, 5, 2, 12.0, swec.SE_GREG_CAL),
        "revjul": lambda: swe.swe_revjul(
            jd,
            swec.SE_GREG_CAL,
            rev_year,
            rev_month,
            rev_day,
            rev_hour,
        ),
        "calc_ut_sun": lambda: swe.swe_calc_ut(jd, swec.SE_SUN, flags, xx, serr),
        "calc_ut_moon": lambda: swe.swe_calc_ut(jd, swec.SE_MOON, flags, xx, serr),
        "houses": lambda: swe.swe_houses(jd, 23.0225, 72.5714, ord("P"), cusps, ascmc),
        "ayanamsa_ut": lambda: swe.swe_get_ayanamsa_ut(jd),
        "deltat": lambda: swe.swe_deltat(jd),
        "sidtime": lambda: swe.swe_sidtime(jd),
        "split_deg": lambda: swe.swe_split_deg(
            123.456789,
            swec.SE_SPLIT_DEG_ROUND_SEC,
            split_deg,
            split_min,
            split_sec,
            split_frac,
            split_sign,
        ),
        "azalt": lambda: swe.swe_azalt(
            jd,
            swec.SE_EQU2HOR,
            xpo,
            1013.25,
            15.0,
            xx,
            xaz,
        ),
        "utc_to_jd": lambda: swe.swe_utc_to_jd(
            2026, 5, 2, 12, 0, 0.0, swec.SE_GREG_CAL, utc_dret, serr
        ),
        "sol_eclipse_when_glob": lambda: swe.swe_sol_eclipse_when_glob(
            jd,
            swec.SEFLG_SWIEPH,
            0,
            dret,
            0,
            serr,
        ),
    }

    generic_double = (c_double * 64)(*([1.0] * 64))
    generic_int = (c_int * 64)(*([1] * 64))
    generic_char = create_string_buffer(b"Sirius", 1024)
    generic_char_out = create_string_buffer(1024)

    def value_for_arg(argtype: object) -> object:
        if argtype is c_double:
            return jd
        if argtype is c_int:
            return flags
        if argtype is c_char:
            return c_char(b"P")
        if argtype is c_char_p:
            return generic_char
        name = getattr(argtype, "__name__", "")
        if name == "LP_c_double":
            return generic_double
        if name in {"LP_c_int", "LP_c_long"}:
            return generic_int
        if name == "LP_c_char":
            return generic_char_out
        return generic_double

    def make_generic_case(function_name: str) -> Callable[[], object]:
        func = getattr(swe, function_name)
        argtypes = _SIGNATURES[function_name][1]
        args = [value_for_arg(argtype) for argtype in argtypes]

        def call() -> object:
            return func(*args)

        return call

    all_cases: dict[str, Callable[[], object]] = {}
    for function_name in sorted(_SIGNATURES):
        all_cases[function_name] = curated_cases.get(
            function_name.removeprefix("swe_"),
            make_generic_case(function_name),
        )

    return all_cases, metadata


def swisseph_cases(distribution: str) -> tuple[dict[str, Callable[[], object]], dict[str, object]]:
    import swisseph as swe

    jd = swe.julday(2026, 5, 2, 12.0, swe.GREG_CAL)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    geopos = (72.5714, 23.0225, 0.0)
    xin = (1.0, 2.0, 3.0)

    metadata = system_metadata(distribution, distribution)
    metadata["module_file"] = getattr(swe, "__file__", None)
    metadata["swiss_ephemeris_version"] = getattr(swe, "version", None)
    metadata["wrapper_version"] = getattr(swe, "__version__", None)

    return {
        "julday": lambda: swe.julday(2026, 5, 2, 12.0, swe.GREG_CAL),
        "revjul": lambda: swe.revjul(jd, swe.GREG_CAL),
        "calc_ut_sun": lambda: swe.calc_ut(jd, swe.SUN, flags),
        "calc_ut_moon": lambda: swe.calc_ut(jd, swe.MOON, flags),
        "houses": lambda: swe.houses(jd, 23.0225, 72.5714, b"P"),
        "ayanamsa_ut": lambda: swe.get_ayanamsa_ut(jd),
        "deltat": lambda: swe.deltat(jd),
        "sidtime": lambda: swe.sidtime(jd),
        "split_deg": lambda: swe.split_deg(123.456789, swe.SPLIT_DEG_ROUND_SEC),
        "azalt": lambda: swe.azalt(jd, swe.EQU2HOR, geopos, 1013.25, 15.0, xin),
        "utc_to_jd": lambda: swe.utc_to_jd(2026, 5, 2, 12, 0, 0.0, swe.GREG_CAL),
        "sol_eclipse_when_glob": lambda: swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, 0, 0),
    }, metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", choices=["ffi", "swisseph"], required=True)
    parser.add_argument("--distribution", default="")
    parser.add_argument("--iterations", type=int, default=5_000)
    parser.add_argument("--warmup", type=int, default=100)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    if args.library == "ffi":
        cases, metadata = ffi_cases()
    else:
        distribution = args.distribution or "pysweph"
        cases, metadata = swisseph_cases(distribution)

    results = [
        asdict(measure(name, fn, args.iterations, args.warmup, args.repeats))
        for name, fn in cases.items()
    ]
    payload = {"system": metadata, "results": results}
    output = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
