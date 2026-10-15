# JPL Moshier Ephemeris Python Version Tracking

**Last verified**: October 15, 2026 (native jpl-ephemeris 1.3.0; release runtimes are rebuilt from that C library, not the 1.1.0 binaries)

## Current Package State

| Attribute | Value |
| --- | --- |
| Python package | `jmeph-ffi` |
| Package version | `1.3.0` |
| Python requirement | `>=3.10` |
| Binding model | Pure Python `ctypes` runtime FFI |
| Native API target | `225` public `jme_*` functions |
| Native constant target | `478` public `JME_*` constants, plus 2 header include guards |
| Native source tree | `jpl-ephemeris-` |
| Runtime binary source | `jpl-moshier-ephemeris-php` prebuilt libs |
| License | `MIT AND CeCILL-B` (project code MIT; bundled CALCEPH CeCILL-B; see `THIRD_PARTY_NOTICES.md`) |
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

- `225/225` ctypes signatures generated from native headers and API inventory
- `478` public `JME_*` constants plus the two header include guards, generated from native headers
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
