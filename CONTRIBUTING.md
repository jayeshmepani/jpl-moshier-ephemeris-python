# Contributing to JPL Moshier Ephemeris Python

This package is a raw `ctypes` wrapper over the native JME C API. Contributions should preserve that low-level, lossless contract.

## Requirements

- Python 3.10 or newer
- Git
- Bundled JME/CALCEPH runtimes, or explicit `JME_LIBRARY_PATH` and `JME_CALCEPH_LIBRARY_PATH`
- Optional local native source tree for surface-audit tests via `JME_SOURCE_PATH`

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/jpl-moshier-ephemeris-python.git
cd jpl-moshier-ephemeris-python
python -m pip install -e ".[dev]"
python scripts/fetch_prebuilt.py
python -m pytest
```

## Quality Checks

```bash
python -m ruff check .
python -m ruff format . --check
python -m pyright
python -m pytest
python -m build
python -m twine check dist/*
```

## Raw API Rules

Do not:

- rename `jme_*` functions;
- rename or alter `JME_*` constant values;
- reorder arguments;
- reshape output buffers in the raw layer;
- hide return codes;
- drop error buffer arguments;
- reimplement astronomy inside Python;
- silently normalize or round outputs.

Do:

- keep the wrapper aligned with `include/jme/jme.h` and `include/jme/jme_extended.h`;
- keep the generated surface at `204` functions and `462` constants unless the native API changes;
- add or update tests when bindings or loader behavior change;
- use the PHP wrapper as the prebuilt runtime source of truth.

## Prebuilt Runtimes

Development can source runtimes from:

```text
Copy from a local checkout of jpl-moshier-ephemeris-php/libs
```

Published runtime source:

```text
https://github.com/jayeshmepani/jpl-moshier-ephemeris-php/releases/tag/prebuilt-libs
```

Refresh bundled runtimes with:

```bash
python scripts/fetch_prebuilt.py
```

Useful environment overrides:

- `JME_PHP_LIBS_PATH`
- `JME_PHP_REPO`
- `JME_PHP_TAG`
- `JME_PHP_ARCHIVE_URL`

## Reporting Bugs

Include:

- Python version
- OS and CPU architecture
- package version
- whether you used bundled libraries or env overrides
- exact traceback or native error text
- minimal reproduction

## License

MIT.
