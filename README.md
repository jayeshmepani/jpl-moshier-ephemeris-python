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

This package takes a different approach: the Python layer is pure Python and
uses runtime FFI through `ctypes`. It does not compile a CPython extension
module and does not reshape the raw C API into a Pythonic convenience API.

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
