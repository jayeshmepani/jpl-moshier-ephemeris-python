# Swiss Ephemeris Python FFI - Upstream Synchronization Report

**Generated**: April 25, 2026  
**Upstream Repository**: [aloistr/swisseph](https://github.com/aloistr/swisseph)

---

## Current Status

This package is the Python `ctypes` sibling of `Swiss-Ephemeris-PHP`.

The Python source layer maps constants and C function signatures directly from
the sibling PHP raw FFI binding, which tracks the checked upstream Swiss
Ephemeris source state.

The bundled native libraries are copied from the same prebuilt binary set used
by `Swiss-Ephemeris-PHP`.

---

## Upstream Swiss Ephemeris Information

| Attribute                        | Value                                                   |
| -------------------------------- | ------------------------------------------------------- |
| **Repository**                   | [aloistr/swisseph](https://github.com/aloistr/swisseph) |
| **Latest Release Tag**           | `v2.10.3final`                                          |
| **Latest Release Date**          | April 14, 2026                                          |
| **Release Commit**               | `af9823f`                                               |
| **Active Branch Checked**        | `master`                                                |
| **Latest Public Commit Checked** | `2f18c14`                                               |
| **Latest Public Commit Date**    | April 18, 2026                                          |
| **Latest Commit Message**        | `fixed bug in semo4200.se1`                             |
| **Internal C Version String**    | `2.10.03`                                               |
| **Upstream Licensing Model**     | AGPL or Swiss Ephemeris Professional License            |

---

## Important Notes

- `v2.10.3final` is the final 2.10.3 release before publication of Swiss Ephemeris 3.0.
- No public `v3.0` release tag was available at the time of this report.
- Upstream had post-release commits after `v2.10.3final` on `master`.
- The runtime `swe_version()` value may still be `2.10.03` because upstream keeps
  `SE_VERSION` at that value in the C header.
- This Python package does not build native Swiss Ephemeris binaries itself in
  normal release flow; it bundles the trusted binaries sourced from the sibling
  PHP package.

---

## Recent Upstream Changes

| Date       | Commit    | Verified Description                                                     |
| ---------- | --------- | ------------------------------------------------------------------------ |
| 2026-04-18 | `2f18c14` | Fixed bug in `semo4200.se1`                                              |
| 2026-04-15 | `5a7de9e` | Added note that DE441 `.se1` files remain backward compatible            |
| 2026-04-15 | `237e6df` | Added 125 newly named asteroids                                          |
| 2026-04-15 | `f971d00` | Added newly named asteroids                                              |
| 2026-04-14 | `af9823f` | `v2.10.3final`; data files created with DE441                            |
| 2026-03-30 | `5d7d8a1` | Fixed output for format `x` and `X` for planetary moons                  |
| 2026-03-24 | `768a403` | Added inactive Delta T helper file for older pre-2.10 releases           |
| 2026-03-24 | `c0ec2c8` | Upgraded data to DE441 while remaining compatible with Swiss Ephemeris 2 |
| 2026-03-11 | `728f9f4` | Fixed old rounding bug in `swe_split_deg()`                              |
| 2026-03-01 | `16e1806` | `roundmin` is now observed in output field `l`                           |

---

## Verification Checklist

- [x] Latest release tag checked: `v2.10.3final`
- [x] Latest release date checked: April 14, 2026
- [x] Latest public upstream commit checked: `2f18c14`
- [x] Internal C version string documented as `2.10.03`
- [x] 348 constants mapped
- [x] 106 function signatures mapped
- [x] Native libraries bundled for 5 supported platforms
- [x] Ruff configured and passing
- [x] Pyright configured and passing
- [x] Pytest suite configured and passing
- [x] Build and Twine package checks passing

---

## Recommended Checks

```bash
python -m ruff check .
python -m ruff format . --check
python -m pyright
python -m pytest
python -m build
python -m twine check dist/*
```

---

## Support & Resources

- **Upstream Source**: [aloistr/swisseph](https://github.com/aloistr/swisseph)
- **Upstream Releases**: [Swiss Ephemeris releases](https://github.com/aloistr/swisseph/releases)
- **Sibling PHP Package**: [Swiss-Ephemeris-PHP](https://github.com/jayeshmepani/Swiss-Ephemeris-PHP)
- **Official Swiss Ephemeris Site**: [astro.com Swiss Ephemeris](https://www.astro.com/swisseph/)
- **Version Tracking**: [VERSION.md](VERSION.md)

