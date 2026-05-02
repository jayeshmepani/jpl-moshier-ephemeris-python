# Swiss Ephemeris Python FFI

[![PyPI version](https://img.shields.io/pypi/v/swisseph-ffi.svg?style=flat-square)](https://pypi.org/project/swisseph-ffi/)
[![Downloads](https://static.pepy.tech/badge/swisseph-ffi)](https://pepy.tech/projects/swisseph-ffi)
[![Python Versions](https://img.shields.io/pypi/pyversions/swisseph-ffi.svg?style=flat-square)](https://pypi.org/project/swisseph-ffi/)
[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue.svg?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Wheel](https://img.shields.io/pypi/wheel/swisseph-ffi?style=flat-square)](https://pypi.org/project/swisseph-ffi/)
[![Status](https://img.shields.io/pypi/status/swisseph-ffi?style=flat-square)](https://pypi.org/project/swisseph-ffi/)

Pure Python `ctypes` runtime-FFI binding for the Swiss Ephemeris C library.

This project is the Python sibling of `Swiss-Ephemeris-PHP`: the wrapper loads
the native Swiss Ephemeris shared library at runtime and exposes the C API as-is.

## Latest Upstream Status

Checked against upstream on **April 25, 2026**.

- **Latest upstream release tag**: `v2.10.3final` released on **April 14, 2026**.
- **Current upstream `master` checked**: commit `2f18c14` from **April 18, 2026** (`fixed bug in semo4200.se1`).
- **Internal Swiss Ephemeris version string**: the upstream C header still defines `SE_VERSION` as `2.10.03`.
- **Bundled native libraries**: sourced from the sibling `Swiss-Ephemeris-PHP` prebuilt libraries.

See [`VERSION.md`](VERSION.md) and [`UPSTREAM_SYNC.md`](UPSTREAM_SYNC.md) for detailed version tracking.

## Design Contract

The raw binding does not:

- recalculate anything;
- round numeric outputs;
- normalize angles;
- reshape output arrays;
- hide return flags;
- convert C output arrays into Python arrays;
- drop `serr` parameters where the C API has them;
- change house cusp indexing;
- create a higher-level astrology API.

Callers pass `ctypes` buffers and pointers exactly as the C API requires.

## Python Support

The project baseline is Python 3.10 and the target support range is Python
3.10 through Python 3.14.

## Installation

```bash
pip install swisseph-ffi
```

## Native Libraries

The package ships the same prebuilt Swiss Ephemeris binaries as
`Swiss-Ephemeris-PHP`:

- `linux-x64/libswe.so`
- `linux-arm64/libswe.so`
- `macos-x64/libswe.dylib`
- `macos-arm64/libswe.dylib`
- `windows-x64/swe.dll`

You can override discovery with `SWISSEPH_LIBRARY_PATH`.

Library search order:

1. `SWISSEPH_LIBRARY_PATH`
2. bundled `swisseph_ffi/libs/<os-arch>/`
3. common system library paths on Linux/macOS

## Why Another Python Package?

Python already has mature Swiss Ephemeris bindings such as `pyswisseph` and
`pysweph`. They are useful and work well for many CPython users.

Those packages use the compiled CPython extension model. That is a valid and
fast approach, but it couples distribution to Python ABI tags, wheel coverage,
and platform-specific builds.

`swisseph-ffi` was created to fill a different gap: a pure Python `ctypes`
runtime-FFI binding that loads the native Swiss Ephemeris shared library and
keeps the public C API exposed as directly as possible. The package ships
prebuilt native libraries for common platforms, while the Python layer remains
independent of CPython extension ABI changes.

This project is intentionally focused on the raw 1:1 C API layer. It is not a
replacement for higher-level astrology libraries; it is a low-level foundation
for users who want direct Swiss Ephemeris calls from Python without a compiled
Python extension module.

## Transparency Against Existing Python Bindings

This package is intentionally explicit about the gap it fills.

| Area | `pyswisseph` | `pysweph` | `swisseph-ffi` |
| --- | --- | --- | --- |
| Binding model | CPython C extension | CPython C extension fork | Pure Python `ctypes` runtime FFI |
| Python ABI coupling | Yes, wheel tags are CPython/version/platform-specific | Yes, wheel tags are CPython/version/platform-specific | No compiled Python extension ABI |
| Latest PyPI release checked | `2.10.3.2`, uploaded June 4, 2023 | `2.10.3.6`, uploaded February 19, 2026 | `1.0.0`, uploaded May 2026 |
| Python support metadata checked | `>=3.5`, but published wheels are still ABI-tagged | `>=3.8`, classifiers/wheels checked through CPython 3.13 | `>=3.10`, tested target 3.10 through 3.14 |
| Install/build risk | May need source build when no matching wheel exists | May need source build when no matching wheel exists | Ships one pure Python wheel plus bundled native libs |
| Raw C API contract | Python extension API | Python extension API with documented breaking changes | Direct `ctypes` signatures and caller-owned buffers |
| Function coverage in this project | Not used as source of truth | Not used as source of truth | 106/106 public Swiss Ephemeris C functions configured |

Known public context:

- `pyswisseph` has a public open issue titled "Error when installing
  pyswisseph using pip on python 3.12".
- `pysweph` was created as a maintained community fork after the original
  project showed maintenance/documentation gaps.
- `pysweph` documents breaking changes from `pyswisseph`, including changed
  house cusp return behavior.
- `pysweph` also states that its test suite was deprecated as of February 6,
  2026 due to `calc` and `houses` function patches.

That is the motivation for `swisseph-ffi`: keep the Python layer runtime-only,
avoid CPython extension ABI churn, ship the native libraries directly, and make
the raw Swiss Ephemeris C surface visible without Pythonic reshaping.

References:

- `pyswisseph` PyPI: <https://pypi.org/project/pyswisseph/2.10.3.2/>
- `pyswisseph` Python 3.12 issue: <https://github.com/astrorigin/pyswisseph/issues/71>
- `pysweph` PyPI: <https://pypi.org/project/pysweph/>

## Quick Start

```python
from swisseph_ffi import SwissEph, SE_GREG_CAL, SE_SUN, SEFLG_SPEED
from swisseph_ffi import c_double, create_string_buffer

swe = SwissEph()

jd = swe.swe_julday(2000, 1, 1, 12.0, SE_GREG_CAL)
xx = (c_double * 6)()
serr = create_string_buffer(256)

ret = swe.swe_calc_ut(jd, SE_SUN, SEFLG_SPEED, xx, serr)
print(ret, list(xx), serr.value)
```

## Scope

This package intentionally starts with the raw 1:1 layer only. A convenience API
can be built separately later without changing the raw ABI binding.

## Development Checks

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format . --check
python -m pyright
python -m pytest
python -m build
python -m twine check dist/*
```

The test suite includes:

- all 106 C functions loaded and signature-checked;
- runtime behavior tests mirrored from `Swiss-Ephemeris-PHP`;
- optional `swetest` parity tests when the CLI and ephemeris files are available.

## License

This package metadata declares **AGPL-3.0-or-later**.

The upstream Swiss Ephemeris C library and ephemeris data are distributed under
Astrodienst's dual licensing model: **AGPL** or **Swiss Ephemeris Professional
License**. If you use Swiss Ephemeris in commercial, closed-source, SaaS, or
public web-service software, review Astrodienst's license terms before use.
