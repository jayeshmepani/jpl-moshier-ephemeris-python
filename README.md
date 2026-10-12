# JPL Moshier Ephemeris Python

[![PyPI version](https://img.shields.io/pypi/v/jmeph-ffi.svg?style=flat-square)](https://pypi.org/project/jmeph-ffi/)
[![Downloads](https://static.pepy.tech/badge/jmeph-ffi)](https://pepy.tech/projects/jmeph-ffi)
[![Python Versions](https://img.shields.io/pypi/pyversions/jmeph-ffi.svg?style=flat-square)](https://pypi.org/project/jmeph-ffi/)
[![License: MIT AND CeCILL-B](https://img.shields.io/badge/license-MIT%20AND%20CeCILL--B-blue.svg?style=flat-square)](#license)
[![Wheel](https://img.shields.io/pypi/wheel/jmeph-ffi?style=flat-square)](https://pypi.org/project/jmeph-ffi/)
[![Status](https://img.shields.io/pypi/status/jmeph-ffi?style=flat-square)](https://pypi.org/project/jmeph-ffi/)

Pure Python `ctypes` runtime FFI binding for the project-owned JPL Moshier Ephemeris C library.

This package wraps the native `jme_*` API directly. It is intended to be a true raw I/O surface: no recalculation, no normalization, no rounding, no reshaping, no dropped buffers, and no hidden status conversion.

## Contract

- Primary public functions: `jme_*`
- Primary public constants: `JME_*`
- Current wrapper target: all `225` public `jme_*` functions tracked by the native API inventory
- Current constant target: all `480` public `JME_*` constants from the native headers
- Native runtimes bundled in the wheel: `jme` plus `calceph`
- No CPython extension module; pure Python loader plus bundled native libraries
- Argument order, pointer ownership, output buffers, and return values are kept as-is from the native C API

## Installation

```bash
pip install jmeph-ffi
```

End users do not need to download native binaries manually. The package ships its bundled `jme` and `calceph` runtimes inbuilt inside the wheel.

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

The local/PHP release source below is for maintainers and package build refresh only, not for normal users.

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

- `225/225` configured ctypes function signatures
- `480/480` generated `JME_*` constants
- import and runtime loading
- basic native contract calls such as version, Julian day conversion, calculation, houses, ayanamsa, Delta-T, split-degree, body naming, and refraction
- optional source-surface audit against the local native `jpl-ephemeris-` tree

## Credits

This package is a binding for [JPL Moshier Ephemeris (JME)](https://github.com/jayeshmepani/jpl-ephemeris) by Jayesh Mepani (Jayesh Patel). JME builds on:

- **JPL DE440 / DE441** ephemerides (NASA/JPL; Park et al. 2021). Kernels are downloaded separately and are redistributed unmodified per the NAIF rules.
- **CALCEPH 5.0.1** (Copyright CNRS, Observatoire de Paris, Observatoire de la Côte d'Azur), used under the CeCILL-B license. Prebuilt CALCEPH runtime libraries are bundled unmodified; license text in [`LICENSES/CeCILL-B.txt`](LICENSES/CeCILL-B.txt); provided without warranty (CeCILL-B Articles 8 and 9); source code at https://calceph.imcce.fr/.
- **Stephen L. Moshier**: plan404 and Astronomical Almanac 5.6 analytical theories (Moshier engine). MIT License by permission of the author (12 October 2026; [record](https://github.com/jayeshmepani/jpl-ephemeris/blob/main/docs/permissions/MOSHIER_PERMISSION.md)). Portions derived from the work of Stephen L. Moshier, incorporated herein by permission of the author.
- **ELP 2000-82B** by M. Chapront-Touzé and J. Chapront (CDS VI/79), evaluated by JME's own code generated from the unmodified CDS files.
- **VSOP87** by P. Bretagnon and G. Francou (CDS VI/81); C code from Greg A. Miller's VSOP87-Multilang (public domain dedication).
- **Jean Meeus**, *Astronomical Algorithms* (formulas cited); **F. Espenak and J. Meeus** (NASA) ΔT polynomials; **ERFA** (BSD 3-Clause, NumFOCUS Foundation) IAU 2000B nutation; **Yale Bright Star Catalogue** (Hoffleit and Warren).

Full credits, terms, and required notice texts: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

**Package license: `MIT AND CeCILL-B`.**

- The original code in this repository (the Python `ctypes` binding, tests and scripts) is licensed under the [MIT License](LICENSE), Copyright (c) 2026 Jayesh Mepani (Jayesh Patel). The `LICENSE` file contains only the MIT text for that code.
- The bundled prebuilt CALCEPH 5.0.1 runtime libraries are licensed under CeCILL-B; the full text is in [`LICENSES/CeCILL-B.txt`](LICENSES/CeCILL-B.txt).
- The bundled JME runtime libraries contain the Moshier material (plan404, AA 5.6), which is distributed under the MIT License by permission of Stephen L. Moshier, 12 October 2026 ([permission record](https://github.com/jayeshmepani/jpl-ephemeris/blob/main/docs/permissions/MOSHIER_PERMISSION.md)). Portions derived from the work of Stephen L. Moshier, incorporated herein by permission of the author.

Third-party components keep their own terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
