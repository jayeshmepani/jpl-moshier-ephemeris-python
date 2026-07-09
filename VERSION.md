# JPL Moshier Ephemeris Python Version Tracking

**Last verified**: May 25, 2026

## Current Package State

| Attribute | Value |
| --- | --- |
| Python package | `jmeph-ffi` |
| Package version | `1.0.1` |
| Python requirement | `>=3.10` |
| Binding model | Pure Python `ctypes` runtime FFI |
| Native API target | `204` public `jme_*` functions |
| Native constant target | `462` public `JME_*` constants |
| Native source tree | `jpl-ephemeris-` |
| Runtime binary source | `jpl-moshier-ephemeris-php` prebuilt libs |
| License | MIT |
| Binding contract | Lossless raw I/O; native argument order, types, buffers, and return values preserved |

## Bundled Runtime Files

| Platform | JME | CALCEPH |
| --- | --- | --- |
| Linux x64 | `libjme.so` | `libcalceph.so` |
| Linux ARM64 | `libjme.so` | `libcalceph.so` |
| macOS x64 | `libjme.dylib` | `libcalceph.dylib` |
| macOS ARM64 | `libjme.dylib` | `libcalceph.dylib` |
| Windows x64 | `jme.dll` | `calceph.dll` |

## Verification Targets

- `204/204` ctypes signatures generated from native headers and API inventory
- `462/462` `JME_*` constants generated from native headers
- runtime loader covers both JME and CALCEPH
- wheel/source package includes bundled runtime directories

## Update Workflow

```bash
python scripts/fetch_prebuilt.py
JME_SOURCE_PATH=/path/to/jpl-ephemeris- php scripts/generate_bindings.php
python -m ruff check .
python -m ruff format . --check
python -m pyright
python -m pytest
python -m build
python -m twine check dist/*
```
