# Swiss Ephemeris Python FFI Version Tracking

This document tracks the Swiss Ephemeris C library source and native binaries
used by this Python `ctypes` wrapper.

**Last verified**: April 25, 2026

---

## Current Version

| Attribute                        | Value                                                   |
| -------------------------------- | ------------------------------------------------------- |
| **Python Package**               | `swisseph-ffi`                                          |
| **Package Version**              | `1.0.0`                                                 |
| **Python Requirement**           | `>=3.10`                                                |
| **Target Python Versions**       | 3.10, 3.11, 3.12, 3.13, 3.14                            |
| **Binding Model**                | Pure Python `ctypes` runtime FFI                        |
| **Upstream Repository**          | [aloistr/swisseph](https://github.com/aloistr/swisseph) |
| **Latest Release Tag**           | `v2.10.3final`                                          |
| **Latest Release Date**          | April 14, 2026                                          |
| **Release Commit**               | `af9823f`                                               |
| **Development Branch Checked**   | `master`                                                |
| **Latest Public Commit Checked** | `2f18c14`                                               |
| **Latest Public Commit Date**    | April 18, 2026                                          |
| **Latest Commit Message**        | `fixed bug in semo4200.se1`                             |
| **Internal C Version String**    | `2.10.03`                                               |
| **Native Binary Source**         | `Swiss-Ephemeris-PHP` bundled/release prebuilt binaries |

---

## FFI Technical Verification

| Area                   | Status                                                                                 |
| ---------------------- | -------------------------------------------------------------------------------------- |
| **Constant Parity**    | 348 constants generated from the sibling PHP raw FFI binding and parity-checked         |
| **Function Coverage**  | 106/106 Swiss Ephemeris public C functions mapped through `ctypes`                     |
| **Signature Parity**   | Return and argument ctypes checked against the sibling PHP C definitions                |
| **Struct Mapping**     | Not required; Swiss Ephemeris uses primitive pointer-based public API                   |
| **Output Buffers**     | Caller-owned `ctypes` buffers and pointers are passed directly                          |
| **Runtime Validation** | Tests cover version, Julian day, Sun, Moon, houses, ayanamsa, Delta T, split, refraction |
| **CLI Parity**         | Optional `swetest` parity tests cover planets, houses, and lunar eclipse behavior       |

**Verified Claim**: the raw binding is a zero-abstraction, 1:1 runtime FFI
mapping. It does not recalculate, round, normalize, reshape arrays, hide flags,
drop `serr`, or change house cusp indexing.

---

## Bundled Native Libraries

The package ships native Swiss Ephemeris libraries for:

| Platform    | Library       |
| ----------- | ------------- |
| Linux x64   | `libswe.so`   |
| Linux ARM64 | `libswe.so`   |
| macOS x64   | `libswe.dylib` |
| macOS ARM64 | `libswe.dylib` |
| Windows x64 | `swe.dll`     |

The Python package reuses the same trusted native binary set as
`Swiss-Ephemeris-PHP`.

---

## Version History

### 1.0.0

- Initial Python `ctypes` runtime-FFI release.
- Python package baseline: `>=3.10`.
- Target support: Python 3.10 through 3.14.
- 348 constants and 106 C function signatures mapped.
- Bundled native libraries for 5 OS/CPU targets.
- Ruff, Pyright, pytest, build, and twine checks configured.
- GitHub Actions added for test and publish workflows.

---

## Upstream Notes

- `v2.10.3final` was released on April 14, 2026.
- The checked upstream `master` state includes post-release commits through
  April 18, 2026.
- The internal C runtime version string remains `2.10.03`, even when using
  `v2.10.3final` or later checked commits.
- The April 2026 upstream update includes DE441 ephemeris file rebuilds and
  related data updates.

---

## Update Workflow

When native Swiss Ephemeris binaries change in the sibling PHP package:

```bash
python scripts/fetch_prebuilt.py
python -m ruff check .
python -m ruff format . --check
python -m pyright
python -m pytest
python -m build
python -m twine check dist/*
```

Use `SWISSEPH_LIBS_RELEASE` to pin the source release:

```bash
SWISSEPH_LIBS_RELEASE=v1.1.0 python scripts/fetch_prebuilt.py
```

On Windows PowerShell:

```powershell
$env:SWISSEPH_LIBS_RELEASE = "v1.1.0"
python scripts/fetch_prebuilt.py
```

---

## Links

- **Upstream Source**: [aloistr/swisseph](https://github.com/aloistr/swisseph)
- **Upstream Releases**: [Swiss Ephemeris releases](https://github.com/aloistr/swisseph/releases)
- **Sibling PHP Package**: [Swiss-Ephemeris-PHP](https://github.com/jayeshmepani/Swiss-Ephemeris-PHP)
- **Official Site**: [astro.com Swiss Ephemeris](https://www.astro.com/swisseph/)

