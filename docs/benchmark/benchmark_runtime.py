"""Strict Swiss Ephemeris benchmark used by the GitHub Actions report.

The FFI side mirrors ``Swiss-Ephemeris-PHP/docs/benchmark/UltimateBenchmark.php``:
106 explicit C API calls, 100 warmup calls, then 1000 measured samples by default.
Comparison packages are measured only where their public Python wrapper API exposes
an equivalent callable safely enough to benchmark without inventing a fake 1:1 API.
"""

from __future__ import annotations

import argparse
import gc
import importlib.metadata
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc
from collections.abc import Callable
from ctypes import c_double, c_long, create_string_buffer
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

StatMap = dict[str, float | int]
CaseMap = dict[str, Callable[[], Any]]


def package_version(distribution: str) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def command_value(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def shell_value(command: str) -> str:
    try:
        return subprocess.check_output(
            command, text=True, stderr=subprocess.DEVNULL, shell=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def first_numeric(values: list[str]) -> float | None:
    for value in values:
        try:
            numeric = float(value)
        except ValueError:
            continue
        if numeric > 0:
            return numeric
    return None


def format_ghz(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".") + " GHz"


def format_bytes(value: int | float) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}".replace(".0 ", " ")
        size /= 1024
    return f"{size:.1f} TB"


def format_instruction_sets(flags: str) -> str:
    text = flags.lower()
    found: list[str] = []
    for needle, label in {
        "avx2": "AVX2",
        "bmi2": "BMI2",
        "sse4_2": "SSE4.2",
        "sse4.2": "SSE4.2",
        "neon": "NEON",
    }.items():
        if needle in text and label not in found:
            found.append(label)
    return ", ".join(found) if found else "Unavailable on runner"


def memory_bytes() -> int | None:
    if hasattr(os, "sysconf"):
        try:
            return int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
        except (OSError, ValueError):
            pass
    if platform.system() == "Windows":
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
            return int(status.ullTotalPhys)
        except (AttributeError, OSError):
            return None
    return None


def system_probe(library: str, distribution: str, swiss_version: str) -> dict[str, Any]:
    os_name = platform.system()
    mem = memory_bytes()
    cpu = platform.processor()
    cores = str(os.cpu_count() or "")
    freq = "Unavailable on runner"
    l3 = "N/A"
    system_model = platform.platform()
    instr = "Unavailable on runner"

    if os_name == "Linux":
        cpu = (
            shell_value(
                "lscpu | awk -F: '/Model name/ {sub(/^[ \\t]+/, \"\", $2); print $2; exit}'"
            )
            or cpu
        )
        cores_probe = shell_value(
            "lscpu | awk -F: '/^CPU\\(s\\)/ {gsub(/ /, \"\", $2); print $2; exit}'"
        )
        cores = f"{cores_probe} Threads" if cores_probe else f"{cores} Threads"
        mhz = first_numeric(
            [
                shell_value(
                    "lscpu | awk -F: '/CPU max MHz/ {gsub(/ /, \"\", $2); print $2; exit}'"
                ),
                shell_value(
                    "cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq 2>/dev/null"
                ),
            ]
        )
        if mhz and mhz > 10000:
            mhz /= 1000
        freq = format_ghz(mhz / 1000) if mhz else freq
        l3 = (
            shell_value("lscpu | awk -F: '/L3 cache/ {sub(/^[ \\t]+/, \"\", $2); print $2; exit}'")
            or l3
        )
        system_model = (
            shell_value("cat /sys/class/dmi/id/product_name 2>/dev/null") or "Generic Linux Node"
        )
        instr = format_instruction_sets(shell_value("lscpu | awk -F: '/Flags/ {print $2; exit}'"))
    elif os_name == "Darwin":
        cpu = command_value(["sysctl", "-n", "machdep.cpu.brand_string"]) or cpu or "Apple Silicon"
        cores_probe = command_value(["sysctl", "-n", "hw.ncpu"])
        cores = f"{cores_probe} Logical Cores" if cores_probe else f"{cores} Logical Cores"
        hz = first_numeric([command_value(["sysctl", "-n", "hw.cpufrequency"])])
        freq = format_ghz(hz / 1_000_000_000) if hz else freq
        l3_bytes = first_numeric([command_value(["sysctl", "-n", "hw.l3cachesize"])])
        l3 = f"{round(l3_bytes / 1024 / 1024)} MB" if l3_bytes else l3
        system_model = command_value(["sysctl", "-n", "hw.model"]) or "Apple Mac"
        instr = (
            "NEON (ARM64)"
            if platform.machine() == "arm64"
            else format_instruction_sets(
                shell_value("sysctl -a 2>/dev/null | grep machdep.cpu.features")
            )
        )
    elif os_name == "Windows":
        cpu = shell_value(
            'powershell -NoProfile -Command "(Get-CimInstance Win32_Processor | '
            'Select-Object -First 1 -ExpandProperty Name)"'
        ) or os.environ.get("PROCESSOR_IDENTIFIER", cpu)
        core_count = shell_value(
            'powershell -NoProfile -Command "(Get-CimInstance Win32_Processor | '
            'Measure-Object -Property NumberOfCores -Sum).Sum"'
        )
        thread_count = shell_value(
            'powershell -NoProfile -Command "(Get-CimInstance Win32_Processor | '
            'Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum"'
        )
        cores = (
            f"{core_count}C / {thread_count}T"
            if core_count and thread_count
            else f"{cores} Threads"
        )
        mhz = first_numeric(
            [
                shell_value(
                    'powershell -NoProfile -Command "(Get-CimInstance Win32_Processor | '
                    'Select-Object -First 1 -ExpandProperty MaxClockSpeed)"'
                )
            ]
        )
        freq = format_ghz(mhz / 1000) if mhz else freq
        l3_kb = first_numeric(
            [
                shell_value(
                    'powershell -NoProfile -Command "(Get-CimInstance Win32_Processor | '
                    'Measure-Object -Property L3CacheSize -Sum).Sum"'
                )
            ]
        )
        l3 = f"{round(l3_kb / 1024)} MB" if l3_kb else l3
        system_model = (
            shell_value(
                'powershell -NoProfile -Command "(Get-CimInstance Win32_ComputerSystem | '
                'Select-Object -First 1 -ExpandProperty Model)"'
            )
            or "Windows Runner"
        )
        instr = (
            shell_value(
                'powershell -NoProfile -Command "$s=@(); '
                "if ([System.Runtime.Intrinsics.X86.Avx2]::IsSupported) {$s+='AVX2'}; "
                "if ([System.Runtime.Intrinsics.X86.Bmi2]::IsSupported) {$s+='BMI2'}; "
                "if ([System.Runtime.Intrinsics.X86.Sse42]::IsSupported) {$s+='SSE4.2'}; "
                "$s -join ', '\""
            )
            or instr
        )

    if not cpu:
        cpu = "Processor probe returned empty value"

    return {
        "cpu": cpu,
        "cores": cores,
        "freq": freq,
        "l3": l3,
        "arch": platform.machine(),
        "instr": instr,
        "ram": format_bytes(mem) if mem else "RAM probe returned empty value",
        "ram_bytes": mem,
        "system": system_model,
        "python": platform.python_version(),
        "python_runtime": sys.version,
        "python_implementation": platform.python_implementation(),
        "python_compiler": platform.python_compiler(),
        "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "date": datetime.now(UTC).isoformat(),
        "library": f"Swiss Ephemeris {swiss_version}",
        "distribution": distribution,
        "distribution_version": package_version(distribution),
        "benchmark_library": library,
        "protocol": "100 warmup + 1000 measurement samples",
    }


def calc_stats(samples: list[float], mem_delta: int) -> StatMap:
    ordered = sorted(samples)
    count = len(ordered)
    mean = statistics.mean(ordered)
    p95_index = min(count - 1, int(count * 0.95))
    return {
        "mean": mean,
        "median": ordered[count // 2],
        "p95": ordered[p95_index],
        "stddev": statistics.pstdev(ordered) if count > 1 else 0.0,
        "min": ordered[0],
        "max": ordered[-1],
        "count": count,
        "mem": mem_delta,
    }


def ratio(ffi: float | int, ext: float | int) -> float:
    if ext == 0:
        return 1.0 if ffi == 0 else 999.9
    value = float(ffi) / float(ext)
    return value if math.isfinite(value) else 999.9


def measure(fn: Callable[[], Any], iterations: int, warmup: int) -> tuple[StatMap, Any]:
    for _ in range(warmup):
        fn()

    samples: list[float] = []
    last_result: Any = None
    gc.disable()
    tracemalloc.start()
    try:
        start_memory = tracemalloc.get_traced_memory()[0]
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            last_result = fn()
            t1 = time.perf_counter_ns()
            samples.append((t1 - t0) / 1000)
        current_memory, peak_memory = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
        gc.enable()
    return calc_stats(
        samples, max(0, peak_memory - start_memory, current_memory - start_memory)
    ), last_result


def ffi_cases() -> tuple[CaseMap, dict[str, Any]]:
    import swisseph_ffi as const
    from swisseph_ffi import SwissEph
    from swisseph_ffi.bindings import _SIGNATURES

    swe = SwissEph()
    jd = 2451545.0
    ipl = 0
    iflag = 2
    p_house = ord("P")

    xx = (c_double * 20)()
    serr = create_string_buffer(256)
    cusps = (c_double * 13)()
    ascmc = (c_double * 10)()
    tret = (c_double * 40)()
    attr = (c_double * 40)()
    ii = (c_long * 20)()
    geopos = (c_double * 10)()
    datm = (c_double * 10)()
    dobs = (c_double * 10)()
    dret = (c_double * 40)()
    s1 = create_string_buffer(512)
    s2 = create_string_buffer(512)
    star = create_string_buffer(b"Sirius", 512)

    geopos[0] = 72.6313
    geopos[1] = 23.1815
    geopos[2] = 0.0

    swe.swe_set_ephe_path(b".")

    def star_buffer() -> Any:
        star.value = b"Sirius"
        return star

    cases: CaseMap = {
        "swe_heliacal_ut": lambda: swe.swe_heliacal_ut(
            jd, geopos, datm, dobs, star_buffer(), 1, iflag, dret, serr
        ),
        "swe_heliacal_pheno_ut": lambda: swe.swe_heliacal_pheno_ut(
            jd, geopos, datm, dobs, star_buffer(), 1, iflag, dret, serr
        ),
        "swe_vis_limit_mag": lambda: swe.swe_vis_limit_mag(
            jd, geopos, datm, dobs, star_buffer(), iflag, dret, serr
        ),
        "swe_heliacal_angle": lambda: swe.swe_heliacal_angle(
            jd, geopos, datm, dobs, iflag, 0.0, 0.0, 0.0, 0.0, 0.0, dret, serr
        ),
        "swe_topo_arcus_visionis": lambda: swe.swe_topo_arcus_visionis(
            jd, geopos, datm, dobs, iflag, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, dret, serr
        ),
        "swe_set_astro_models": lambda: swe.swe_set_astro_models(b"test", 0),
        "swe_get_astro_models": lambda: swe.swe_get_astro_models(s1, s2, 0),
        "swe_version": lambda: swe.swe_version(s1),
        "swe_get_library_path": lambda: swe.swe_get_library_path(s1),
        "swe_calc": lambda: swe.swe_calc(jd, ipl, iflag, xx, serr),
        "swe_calc_ut": lambda: swe.swe_calc_ut(jd, ipl, iflag, xx, serr),
        "swe_calc_pctr": lambda: swe.swe_calc_pctr(jd, ipl, 14, iflag, xx, serr),
        "swe_solcross": lambda: swe.swe_solcross(0.0, jd, iflag, serr),
        "swe_solcross_ut": lambda: swe.swe_solcross_ut(0.0, jd, iflag, serr),
        "swe_mooncross": lambda: swe.swe_mooncross(0.0, jd, iflag, serr),
        "swe_mooncross_ut": lambda: swe.swe_mooncross_ut(0.0, jd, iflag, serr),
        "swe_mooncross_node": lambda: swe.swe_mooncross_node(jd, iflag, xx, xx, serr),
        "swe_mooncross_node_ut": lambda: swe.swe_mooncross_node_ut(jd, iflag, xx, xx, serr),
        "swe_helio_cross": lambda: swe.swe_helio_cross(ipl, 0.0, jd, iflag, 1, xx, serr),
        "swe_helio_cross_ut": lambda: swe.swe_helio_cross_ut(ipl, 0.0, jd, iflag, 1, xx, serr),
        "swe_fixstar": lambda: swe.swe_fixstar(star_buffer(), jd, iflag, xx, serr),
        "swe_fixstar_ut": lambda: swe.swe_fixstar_ut(star_buffer(), jd, iflag, xx, serr),
        "swe_fixstar_mag": lambda: swe.swe_fixstar_mag(star_buffer(), xx, serr),
        "swe_fixstar2": lambda: swe.swe_fixstar2(star_buffer(), jd, iflag, xx, serr),
        "swe_fixstar2_ut": lambda: swe.swe_fixstar2_ut(star_buffer(), jd, iflag, xx, serr),
        "swe_fixstar2_mag": lambda: swe.swe_fixstar2_mag(star_buffer(), xx, serr),
        "swe_close": lambda: swe.swe_close(),
        "swe_set_ephe_path": lambda: swe.swe_set_ephe_path(b"."),
        "swe_set_jpl_file": lambda: swe.swe_set_jpl_file(b"de431.eph"),
        "swe_get_planet_name": lambda: swe.swe_get_planet_name(ipl, s1),
        "swe_set_topo": lambda: swe.swe_set_topo(72.6, 23.1, 0.0),
        "swe_set_sid_mode": lambda: swe.swe_set_sid_mode(const.SE_SIDM_FAGAN_BRADLEY, 0.0, 0.0),
        "swe_get_ayanamsa_ex": lambda: swe.swe_get_ayanamsa_ex(jd, iflag, xx, serr),
        "swe_get_ayanamsa_ex_ut": lambda: swe.swe_get_ayanamsa_ex_ut(jd, iflag, xx, serr),
        "swe_get_ayanamsa": lambda: swe.swe_get_ayanamsa(jd),
        "swe_get_ayanamsa_ut": lambda: swe.swe_get_ayanamsa_ut(jd),
        "swe_get_ayanamsa_name": lambda: swe.swe_get_ayanamsa_name(1),
        "swe_get_current_file_data": lambda: swe.swe_get_current_file_data(1, xx, xx, ii),
        "swe_date_conversion": lambda: swe.swe_date_conversion(2024, 4, 30, 12.0, b"g", xx),
        "swe_julday": lambda: swe.swe_julday(2024, 4, 30, 12.0, 1),
        "swe_revjul": lambda: swe.swe_revjul(jd, 1, ii, ii, ii, xx),
        "swe_utc_to_jd": lambda: swe.swe_utc_to_jd(2024, 4, 30, 12, 0, 0.0, 1, dret, serr),
        "swe_jdet_to_utc": lambda: swe.swe_jdet_to_utc(jd, 1, ii, ii, ii, ii, ii, xx),
        "swe_jdut1_to_utc": lambda: swe.swe_jdut1_to_utc(jd, 1, ii, ii, ii, ii, ii, xx),
        "swe_utc_time_zone": lambda: swe.swe_utc_time_zone(
            2024, 4, 30, 12, 0, 0.0, 5.5, ii, ii, ii, ii, ii, xx
        ),
        "swe_houses": lambda: swe.swe_houses(jd, 23.1, 72.6, p_house, cusps, ascmc),
        "swe_houses_ex": lambda: swe.swe_houses_ex(jd, iflag, 23.1, 72.6, p_house, cusps, ascmc),
        "swe_houses_ex2": lambda: swe.swe_houses_ex2(
            jd, iflag, 23.1, 72.6, p_house, cusps, ascmc, xx, xx, serr
        ),
        "swe_houses_armc": lambda: swe.swe_houses_armc(120.0, 23.1, 23.4, p_house, cusps, ascmc),
        "swe_houses_armc_ex2": lambda: swe.swe_houses_armc_ex2(
            120.0, 23.1, 23.4, p_house, cusps, ascmc, xx, xx, serr
        ),
        "swe_house_pos": lambda: swe.swe_house_pos(120.0, 23.1, 23.4, p_house, xx, serr),
        "swe_house_name": lambda: swe.swe_house_name(p_house),
        "swe_gauquelin_sector": lambda: swe.swe_gauquelin_sector(
            jd, ipl, star_buffer(), iflag, 0, geopos, 1013.25, 15.0, xx, serr
        ),
        "swe_sol_eclipse_where": lambda: swe.swe_sol_eclipse_where(jd, iflag, geopos, attr, serr),
        "swe_lun_occult_where": lambda: swe.swe_lun_occult_where(
            jd, ipl, star_buffer(), iflag, geopos, attr, serr
        ),
        "swe_sol_eclipse_how": lambda: swe.swe_sol_eclipse_how(jd, iflag, geopos, attr, serr),
        "swe_sol_eclipse_when_loc": lambda: swe.swe_sol_eclipse_when_loc(
            jd, iflag, geopos, tret, attr, 0, serr
        ),
        "swe_lun_occult_when_loc": lambda: swe.swe_lun_occult_when_loc(
            jd, ipl, star_buffer(), iflag, geopos, tret, attr, 0, serr
        ),
        "swe_sol_eclipse_when_glob": lambda: swe.swe_sol_eclipse_when_glob(
            jd, iflag, 0, tret, 0, serr
        ),
        "swe_lun_occult_when_glob": lambda: swe.swe_lun_occult_when_glob(
            jd, ipl, star_buffer(), iflag, 0, tret, 0, serr
        ),
        "swe_lun_eclipse_how": lambda: swe.swe_lun_eclipse_how(jd, iflag, geopos, attr, serr),
        "swe_lun_eclipse_when": lambda: swe.swe_lun_eclipse_when(jd, iflag, 0, tret, 0, serr),
        "swe_lun_eclipse_when_loc": lambda: swe.swe_lun_eclipse_when_loc(
            jd, iflag, geopos, tret, attr, 0, serr
        ),
        "swe_pheno": lambda: swe.swe_pheno(jd, ipl, iflag, attr, serr),
        "swe_pheno_ut": lambda: swe.swe_pheno_ut(jd, ipl, iflag, attr, serr),
        "swe_refrac": lambda: swe.swe_refrac(45.0, 1013.25, 15.0, 0),
        "swe_refrac_extended": lambda: swe.swe_refrac_extended(
            45.0, 0.0, 1013.25, 15.0, 0.0065, 0, xx
        ),
        "swe_set_lapse_rate": lambda: swe.swe_set_lapse_rate(0.0065),
        "swe_azalt": lambda: swe.swe_azalt(jd, 0, geopos, 1013.25, 15.0, xx, xx),
        "swe_azalt_rev": lambda: swe.swe_azalt_rev(jd, 0, geopos, xx, xx),
        "swe_rise_trans_true_hor": lambda: swe.swe_rise_trans_true_hor(
            jd, ipl, star_buffer(), iflag, 1, geopos, 1013.25, 15.0, 0.0, tret, serr
        ),
        "swe_rise_trans": lambda: swe.swe_rise_trans(
            jd, ipl, star_buffer(), iflag, 1, geopos, 1013.25, 15.0, tret, serr
        ),
        "swe_nod_aps": lambda: swe.swe_nod_aps(jd, ipl, iflag, 0, xx, xx, xx, xx, serr),
        "swe_nod_aps_ut": lambda: swe.swe_nod_aps_ut(jd, ipl, iflag, 0, xx, xx, xx, xx, serr),
        "swe_get_orbital_elements": lambda: swe.swe_get_orbital_elements(
            jd, ipl, iflag, dret, serr
        ),
        "swe_orbit_max_min_true_distance": lambda: swe.swe_orbit_max_min_true_distance(
            jd, ipl, iflag, xx, xx, xx, serr
        ),
        "swe_deltat": lambda: swe.swe_deltat(jd),
        "swe_deltat_ex": lambda: swe.swe_deltat_ex(jd, iflag, serr),
        "swe_time_equ": lambda: swe.swe_time_equ(jd, xx, serr),
        "swe_lmt_to_lat": lambda: swe.swe_lmt_to_lat(jd, 72.6, xx, serr),
        "swe_lat_to_lmt": lambda: swe.swe_lat_to_lmt(jd, 72.6, xx, serr),
        "swe_sidtime0": lambda: swe.swe_sidtime0(jd, 23.4, 0.0),
        "swe_sidtime": lambda: swe.swe_sidtime(jd),
        "swe_set_interpolate_nut": lambda: swe.swe_set_interpolate_nut(1),
        "swe_cotrans": lambda: swe.swe_cotrans(xx, xx, 23.4),
        "swe_cotrans_sp": lambda: swe.swe_cotrans_sp(xx, xx, 23.4),
        "swe_get_tid_acc": lambda: swe.swe_get_tid_acc(),
        "swe_set_tid_acc": lambda: swe.swe_set_tid_acc(0.0),
        "swe_set_delta_t_userdef": lambda: swe.swe_set_delta_t_userdef(0.0),
        "swe_degnorm": lambda: swe.swe_degnorm(370.0),
        "swe_radnorm": lambda: swe.swe_radnorm(7.0),
        "swe_rad_midp": lambda: swe.swe_rad_midp(1.0, 2.0),
        "swe_deg_midp": lambda: swe.swe_deg_midp(10.0, 20.0),
        "swe_split_deg": lambda: swe.swe_split_deg(123.456, 1, ii, ii, ii, xx, ii),
        "swe_csnorm": lambda: swe.swe_csnorm(123456),
        "swe_difcsn": lambda: swe.swe_difcsn(123456, 654321),
        "swe_difdegn": lambda: swe.swe_difdegn(100.0, 200.0),
        "swe_difcs2n": lambda: swe.swe_difcs2n(123456, 654321),
        "swe_difdeg2n": lambda: swe.swe_difdeg2n(100.0, 200.0),
        "swe_difrad2n": lambda: swe.swe_difrad2n(1.0, 2.0),
        "swe_csroundsec": lambda: swe.swe_csroundsec(123456),
        "swe_d2l": lambda: swe.swe_d2l(123.456),
        "swe_day_of_week": lambda: swe.swe_day_of_week(jd),
        "swe_cs2timestr": lambda: swe.swe_cs2timestr(123456, ord(":"), 0, s1),
        "swe_cs2lonlatstr": lambda: swe.swe_cs2lonlatstr(123456, b"E", b"W", s1),
        "swe_cs2degstr": lambda: swe.swe_cs2degstr(123456, s1),
    }

    if len(cases) != 106 or set(cases) != set(_SIGNATURES):
        missing = sorted(set(_SIGNATURES) - set(cases))
        extra = sorted(set(cases) - set(_SIGNATURES))
        raise RuntimeError(f"Benchmark function map mismatch. missing={missing} extra={extra}")

    version_buffer = create_string_buffer(256)
    swe.swe_version(version_buffer)
    metadata = system_probe(
        "swisseph-ffi", "swisseph-ffi", version_buffer.value.decode(errors="replace")
    )
    metadata["native_library"] = str(swe.library_path)
    metadata["configured_function_count"] = len(_SIGNATURES)
    metadata["benchmarked_function_count"] = len(cases)
    return cases, metadata


def extension_cases(distribution: str) -> tuple[CaseMap, dict[str, Any]]:
    import swisseph as swe

    jd = swe.julday(2024, 4, 30, 12.0, swe.GREG_CAL)
    flags = getattr(swe, "FLG_SWIEPH", 2)
    geopos = (72.6313, 23.1815, 0.0)
    xin = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    xx = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    ipl = getattr(swe, "SUN", 0)
    star = b"Sirius"
    datm = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    dobs = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    metadata = system_probe("swisseph", distribution, str(getattr(swe, "version", "unknown")))
    metadata["module_file"] = getattr(swe, "__file__", "")
    metadata["wrapper_version"] = getattr(swe, "__version__", "")
    metadata["configured_function_count"] = 106

    cases: CaseMap = {
        "swe_calc_ut": lambda: swe.calc_ut(jd, ipl, flags),
        "swe_julday": lambda: swe.julday(2024, 4, 30, 12.0, swe.GREG_CAL),
        "swe_revjul": lambda: swe.revjul(jd, swe.GREG_CAL),
        "swe_get_ayanamsa": lambda: swe.get_ayanamsa(jd),
        "swe_get_ayanamsa_ut": lambda: swe.get_ayanamsa_ut(jd),
        "swe_deltat": lambda: swe.deltat(jd),
        "swe_sidtime": lambda: swe.sidtime(jd),
        "swe_sidtime0": lambda: swe.sidtime0(jd, 23.4, 0.0),
        "swe_degnorm": lambda: swe.degnorm(370.0),
        "swe_radnorm": lambda: swe.radnorm(7.0),
        "swe_rad_midp": lambda: swe.rad_midp(1.0, 2.0),
        "swe_deg_midp": lambda: swe.deg_midp(10.0, 20.0),
        "swe_difdegn": lambda: swe.difdegn(100.0, 200.0),
        "swe_difdeg2n": lambda: swe.difdeg2n(100.0, 200.0),
        "swe_difrad2n": lambda: swe.difrad2n(1.0, 2.0),
        "swe_csroundsec": lambda: swe.csroundsec(123456),
        "swe_d2l": lambda: swe.d2l(123.456),
        "swe_day_of_week": lambda: swe.day_of_week(jd),
        "swe_houses": lambda: swe.houses(jd, 23.1, 72.6, b"P"),
        "swe_houses_ex": lambda: swe.houses_ex(jd, 23.1, 72.6, b"P", flags),
        "swe_house_pos": lambda: swe.house_pos(120.0, 23.1, 23.4, (0.0, 0.0), b"P"),
        "swe_house_name": lambda: swe.house_name(b"P"),
        "swe_azalt": lambda: swe.azalt(jd, getattr(swe, "EQU2HOR", 1), geopos, 1013.25, 15.0, xin),
        "swe_azalt_rev": lambda: swe.azalt_rev(jd, getattr(swe, "HOR2EQU", 3), geopos, 0.0, 0.0),
        "swe_refrac": lambda: swe.refrac(45.0, 1013.25, 15.0, 0),
        "swe_split_deg": lambda: swe.split_deg(123.456, getattr(swe, "SPLIT_DEG_ROUND_SEC", 1)),
        "swe_utc_to_jd": lambda: swe.utc_to_jd(2024, 4, 30, 12, 0, 0.0, swe.GREG_CAL),
        "swe_calc": lambda: swe.calc(jd, ipl, flags),
        "swe_calc_pctr": lambda: swe.calc_pctr(jd, ipl, 14, flags),
        "swe_solcross": lambda: swe.solcross(0.0, jd, flags),
        "swe_solcross_ut": lambda: swe.solcross_ut(0.0, jd, flags),
        "swe_mooncross": lambda: swe.mooncross(0.0, jd, flags),
        "swe_mooncross_ut": lambda: swe.mooncross_ut(0.0, jd, flags),
        "swe_mooncross_node": lambda: swe.mooncross_node(jd, flags),
        "swe_mooncross_node_ut": lambda: swe.mooncross_node_ut(jd, flags),
        "swe_helio_cross": lambda: swe.helio_cross(ipl, 0.0, jd, flags, 1),
        "swe_helio_cross_ut": lambda: swe.helio_cross_ut(ipl, 0.0, jd, flags, 1),
        "swe_fixstar": lambda: swe.fixstar(star, jd, flags),
        "swe_fixstar_ut": lambda: swe.fixstar_ut(star, jd, flags),
        "swe_fixstar_mag": lambda: swe.fixstar_mag(star),
        "swe_fixstar2": lambda: swe.fixstar2(star, jd, flags),
        "swe_fixstar2_ut": lambda: swe.fixstar2_ut(star, jd, flags),
        "swe_fixstar2_mag": lambda: swe.fixstar2_mag(star),
        "swe_close": lambda: swe.close(),
        "swe_set_ephe_path": lambda: swe.set_ephe_path(b"."),
        "swe_get_library_path": lambda: swe.get_library_path(),
        "swe_set_jpl_file": lambda: swe.set_jpl_file(b"de431.eph"),
        "swe_get_planet_name": lambda: swe.get_planet_name(ipl),
        "swe_set_topo": lambda: swe.set_topo(72.6, 23.1, 0.0),
        "swe_set_sid_mode": lambda: swe.set_sid_mode(getattr(swe, "SIDM_FAGAN_BRADLEY", 0), 0.0, 0.0),
        "swe_get_ayanamsa_ex": lambda: swe.get_ayanamsa_ex(jd, flags),
        "swe_get_ayanamsa_ex_ut": lambda: swe.get_ayanamsa_ex_ut(jd, flags),
        "swe_get_ayanamsa_name": lambda: swe.get_ayanamsa_name(1),
        "swe_get_current_file_data": lambda: swe.get_current_file_data(1),
        "swe_date_conversion": lambda: swe.date_conversion(2024, 4, 30, 12.0, b"g"),
        "swe_jdet_to_utc": lambda: swe.jdet_to_utc(jd, 1),
        "swe_jdut1_to_utc": lambda: swe.jdut1_to_utc(jd, 1),
        "swe_utc_time_zone": lambda: swe.utc_time_zone(2024, 4, 30, 12, 0, 0.0, 5.5),
        "swe_houses_armc": lambda: swe.houses_armc(120.0, 23.1, 23.4, b"P"),
        "swe_houses_armc_ex2": lambda: swe.houses_armc_ex2(120.0, 23.1, 23.4, b"P"),
        "swe_houses_ex2": lambda: swe.houses_ex2(jd, flags, 23.1, 72.6, b"P"),
        "swe_gauquelin_sector": lambda: swe.gauquelin_sector(jd, ipl, star, flags, 0, geopos, 1013.25, 15.0),
        "swe_sol_eclipse_where": lambda: swe.sol_eclipse_where(jd, flags, geopos),
        "swe_lun_occult_where": lambda: swe.lun_occult_where(jd, ipl, star, flags, geopos),
        "swe_sol_eclipse_how": lambda: swe.sol_eclipse_how(jd, flags, geopos),
        "swe_sol_eclipse_when_loc": lambda: swe.sol_eclipse_when_loc(jd, flags, geopos, 0),
        "swe_lun_occult_when_loc": lambda: swe.lun_occult_when_loc(jd, ipl, star, flags, geopos, 0),
        "swe_sol_eclipse_when_glob": lambda: swe.sol_eclipse_when_glob(jd, flags, 0),
        "swe_lun_occult_when_glob": lambda: swe.lun_occult_when_glob(jd, ipl, star, flags, 0),
        "swe_lun_eclipse_how": lambda: swe.lun_eclipse_how(jd, flags, geopos),
        "swe_lun_eclipse_when": lambda: swe.lun_eclipse_when(jd, flags, 0),
        "swe_lun_eclipse_when_loc": lambda: swe.lun_eclipse_when_loc(jd, flags, geopos, 0),
        "swe_pheno": lambda: swe.pheno(jd, ipl, flags),
        "swe_pheno_ut": lambda: swe.pheno_ut(jd, ipl, flags),
        "swe_refrac_extended": lambda: swe.refrac_extended(45.0, 0.0, 1013.25, 15.0, 0.0065, 0),
        "swe_set_lapse_rate": lambda: swe.set_lapse_rate(0.0065),
        "swe_rise_trans_true_hor": lambda: swe.rise_trans_true_hor(jd, ipl, star, flags, 1, geopos, 1013.25, 15.0, 0.0),
        "swe_rise_trans": lambda: swe.rise_trans(jd, ipl, star, flags, 1, geopos, 1013.25, 15.0),
        "swe_nod_aps": lambda: swe.nod_aps(jd, ipl, flags, 0),
        "swe_nod_aps_ut": lambda: swe.nod_aps_ut(jd, ipl, flags, 0),
        "swe_get_orbital_elements": lambda: swe.get_orbital_elements(jd, ipl, flags),
        "swe_orbit_max_min_true_distance": lambda: swe.orbit_max_min_true_distance(jd, ipl, flags),
        "swe_deltat_ex": lambda: swe.deltat_ex(jd, flags),
        "swe_time_equ": lambda: swe.time_equ(jd),
        "swe_lmt_to_lat": lambda: swe.lmt_to_lat(jd, 72.6),
        "swe_lat_to_lmt": lambda: swe.lat_to_lmt(jd, 72.6),
        "swe_cotrans": lambda: swe.cotrans(xx, 23.4),
        "swe_cotrans_sp": lambda: swe.cotrans_sp(xx, 23.4),
        "swe_get_tid_acc": lambda: swe.get_tid_acc(),
        "swe_set_tid_acc": lambda: swe.set_tid_acc(0.0),
        "swe_set_delta_t_userdef": lambda: swe.set_delta_t_userdef(0.0),
        "swe_csnorm": lambda: swe.csnorm(123456),
        "swe_difcsn": lambda: swe.difcsn(123456, 654321),
        "swe_difcs2n": lambda: swe.difcs2n(123456, 654321),
        "swe_cs2timestr": lambda: swe.cs2timestr(123456, 58, 0),
        "swe_cs2lonlatstr": lambda: swe.cs2lonlatstr(123456, b"E", b"W"),
        "swe_cs2degstr": lambda: swe.cs2degstr(123456),
        "swe_heliacal_ut": lambda: swe.heliacal_ut(jd, geopos, datm, dobs, star, 1, flags),
        "swe_heliacal_pheno_ut": lambda: swe.heliacal_pheno_ut(jd, geopos, datm, dobs, star, 1, flags),
        "swe_vis_limit_mag": lambda: swe.vis_limit_mag(jd, geopos, datm, dobs, star, flags),
    }

    safe_cases = {name: fn for name, fn in cases.items() if hasattr(swe, name.removeprefix("swe_"))}
    metadata["benchmarked_function_count"] = len(safe_cases)
    return safe_cases, metadata


def run_cases(cases: CaseMap, iterations: int, warmup: int, slot: str) -> dict[str, dict[str, Any]]:
    import sys
    results: dict[str, dict[str, Any]] = {}
    for name, fn in cases.items():
        try:
            stats, _last_result = measure(fn, iterations, warmup)
        except Exception as exc:
            results[name] = {slot: None, "error": f"{type(exc).__name__}: {exc}"}
            print(f"{name}: ERR {type(exc).__name__}: {exc}")
            sys.stdout.flush()
            continue
        results[name] = {slot: stats}
        print(f"{name}: {slot.upper()} {stats['mean']:.2f} us")
        sys.stdout.flush()
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", choices=["ffi", "swisseph"], required=True)
    parser.add_argument("--distribution", default="")
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--warmup", type=int, default=100)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    if args.library == "ffi":
        cases, metadata = ffi_cases()
        results = run_cases(cases, args.iterations, args.warmup, "ffi")
    else:
        distribution = args.distribution or "pysweph"
        cases, metadata = extension_cases(distribution)
        results = run_cases(cases, args.iterations, args.warmup, "ext")

    payload = {"system": metadata, "results": results}
    output = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
