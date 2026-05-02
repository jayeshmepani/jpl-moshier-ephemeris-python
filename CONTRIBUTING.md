# Contributing to Swiss Ephemeris Python FFI

Thank you for considering a contribution.

This package is intentionally a raw, zero-abstraction `ctypes` binding to the
Swiss Ephemeris C API. Contributions should preserve that design.

## Requirements

- Python 3.10 or newer
- Git
- The bundled native Swiss Ephemeris libraries, or a custom library path set via
  `SWISSEPH_LIBRARY_PATH`

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/Swiss-Ephemeris-Python.git
cd Swiss-Ephemeris-Python
python -m pip install -e ".[dev]"
python -m pytest
```

## Quality Checks

Run the full local check set before opening a pull request:

```bash
python -m ruff check .
python -m ruff format . --check
python -m pyright
python -m pytest
python -m build
python -m twine check dist/*
```

## 1:1 C API Compatibility

The raw binding must remain a direct C API mapping.

Do not:

- change Swiss Ephemeris function names;
- rename or remove constants;
- change constant values;
- reshape output arrays into Python arrays in the raw layer;
- hide return flags;
- drop `serr` parameters;
- normalize angles;
- round numeric outputs;
- reimplement calculations;
- change house cusp indexing;
- add high-level astrology APIs to the raw binding.

Do:

- keep constants aligned with upstream `swephexp.h`;
- keep `ctypes` signatures aligned with the C declarations;
- pass caller-owned buffers and pointers directly;
- add tests when touching bindings;
- run parity checks against `Swiss-Ephemeris-PHP` and `swetest` where possible.

## Native Libraries

The Python package bundles native libraries under:

```text
src/swisseph_ffi/libs/
```

These binaries are sourced from the sibling `Swiss-Ephemeris-PHP` package. Do
not replace them casually. Native binary updates should be tied to an upstream
Swiss Ephemeris sync or an explicit platform support fix.

To refresh binaries from a known PHP package release:

```bash
SWISSEPH_LIBS_RELEASE=v1.1.0 python scripts/fetch_prebuilt.py
```

On Windows PowerShell:

```powershell
$env:SWISSEPH_LIBS_RELEASE = "v1.1.0"
python scripts/fetch_prebuilt.py
```

## Reporting Bugs

Please include:

- Python version;
- OS and CPU architecture;
- package version;
- whether you use bundled libraries or `SWISSEPH_LIBRARY_PATH`;
- exact error message or stack trace;
- minimal code to reproduce.

## Release Process

Releases follow semantic versioning:

- **MAJOR** for breaking API changes or major upstream compatibility changes.
- **MINOR** for backward-compatible features or platform additions.
- **PATCH** for bug fixes and documentation corrections.

The first public release is `v1.0.0`.

## License

This repository is licensed under **AGPL-3.0-or-later**.

The upstream Swiss Ephemeris C library and ephemeris files are distributed under
Astrodienst's dual licensing model: AGPL or Swiss Ephemeris Professional
License. Commercial, closed-source, SaaS, or public web-service usage may
require a professional license from Astrodienst.

