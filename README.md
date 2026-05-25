# JPL Moshier Ephemeris Python

[![PyPI version](https://img.shields.io/pypi/v/jpl-moshier-ephemeris-python.svg?style=flat-square)](https://pypi.org/project/jpl-moshier-ephemeris-python/)
[![Python Versions](https://img.shields.io/pypi/pyversions/jpl-moshier-ephemeris-python.svg?style=flat-square)](https://pypi.org/project/jpl-moshier-ephemeris-python/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)

Pure Python `ctypes` runtime FFI binding for the project-owned JPL Moshier Ephemeris C library.

This package wraps the native `jme_*` API directly. It is intended to be a true raw I/O surface: no recalculation, no normalization, no rounding, no reshaping, no dropped buffers, and no hidden status conversion.

## Contract

- Primary public functions: `jme_*`
- Primary public constants: `JME_*`
- Current wrapper target: all `204` public `jme_*` functions tracked by the native API inventory
- Current constant target: all `462` public `JME_*` constants from the native headers
- Native runtimes bundled in the wheel: `jme` plus `calceph`
- No CPython extension module; pure Python loader plus bundled native libraries
- Argument order, pointer ownership, output buffers, and return values are kept as-is from the native C API

## Installation

```bash
pip install jpl-moshier-ephemeris-python
```

## Native Libraries

The package bundles the same prebuilt runtimes as the PHP wrapper:

- `linux-x64/libjme.so`
- `linux-x64/libcalceph.so`
- `linux-arm64/libjme.so`
- `linux-arm64/libcalceph.so`
- `macos-x64/libjme.dylib`
- `macos-x64/libcalceph.dylib`
- `macos-arm64/libjme.dylib`
- `macos-arm64/libcalceph.dylib`
- `windows-x64/jme.dll`
- `windows-x64/calceph.dll`

Local source for those prebuilt runtimes during development:

```text
Copy from a local checkout of jpl-moshier-ephemeris-php/libs
```

Published runtime source:

```text
https://github.com/jayeshmepani/jpl-moshier-ephemeris-php/releases/tag/prebuilt-libs
```

You can override discovery with:

- `JME_LIBRARY_PATH`
- `JME_CALCEPH_LIBRARY_PATH`

Search order:

1. explicit environment override
2. bundled `src/jpl_moshier_ephemeris/libs/<platform>/`
3. common system library paths

## Quick Start

```python
from jpl_moshier_ephemeris import (
    JME_BODY_SUN,
    JME_CALC_SPEED,
    JME_CALENDAR_GREGORIAN,
    JmeEph,
    c_double,
    create_string_buffer,
)

jme = JmeEph()

jd = jme.jme_julian_day(2000, 1, 1, 12.0, JME_CALENDAR_GREGORIAN)
xx = (c_double * 6)()
err = create_string_buffer(256)

rc = jme.jme_calc_ut(jd, JME_BODY_SUN, JME_CALC_SPEED, xx, err)
print(rc, list(xx), err.value.decode())
```

## Development

```bash
python -m pip install -e ".[dev]"
python scripts/fetch_prebuilt.py
python -m ruff check .
python -m ruff format . --check
python -m pyright
python -m pytest
python -m build
python -m twine check dist/*
```

The test suite verifies:

- `204/204` configured ctypes function signatures
- `462/462` generated `JME_*` constants
- import and runtime loading
- basic native contract calls such as version, Julian day conversion, calculation, houses, ayanamsa, Delta-T, split-degree, body naming, and refraction
- optional source-surface audit against the local native `jpl-ephemeris-` tree

## License

MIT. The Python package and the project-owned JME native library are intended to remain under MIT-compatible distribution.
