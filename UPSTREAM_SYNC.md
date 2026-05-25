# JPL Moshier Ephemeris Python Sync Notes

**Generated**: May 25, 2026

## Source of Truth

This Python package is synchronized against two local/project sources:

1. Native C library source:
   `jpl-ephemeris-`
2. PHP wrapper prebuilt runtime source:
   `jpl-moshier-ephemeris-php`

## Current Sync Targets

| Area | Target |
| --- | --- |
| Public functions | `204` `jme_*` entries from `docs/API_REFERENCE.md` |
| Public constants | `462` `JME_*` constants from `include/jme/jme.h` and `include/jme/jme_extended.h` |
| Bundled runtimes | same platform runtime set as the PHP wrapper |
| JME runtime names | `libjme.so`, `libjme.dylib`, `jme.dll` |
| CALCEPH runtime names | `libcalceph.so`, `libcalceph.dylib`, `calceph.dll` |
| Python wrapper rule | lossless raw I/O only; no Python-side normalization, rounding, or reshaping |

## Runtime Source

Local development source:

```text
/home/shreesoftech/projects/test1/astro_packages/user-ffi-wrappers/jpl-moshier-ephemeris-php/libs
```

Published runtime source:

```text
https://github.com/jayeshmepani/jpl-moshier-ephemeris-php/releases/tag/prebuilt-libs
```

## Required Checks

- regenerate `bindings.py` and `constants.py` from the native headers when the C API changes
- keep the Python export surface aligned with the generated files
- keep runtime packaging aligned with the PHP wrapper release assets or repo archive tag
- verify tests still pass on Linux, macOS, and Windows
