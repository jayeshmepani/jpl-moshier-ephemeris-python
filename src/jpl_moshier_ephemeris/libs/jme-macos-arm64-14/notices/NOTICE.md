# NOTICE

JPL Moshier Ephemeris (JME)
Copyright (c) 2026 Jayesh Mepani (Jayesh Patel). Licensed under the MIT License (see `LICENSE`).

This product includes or is derived from the following. Full terms, sources
and file locations are in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

* **Moshier theories.** Portions derived from the work of Stephen L. Moshier,
  incorporated herein by permission of the author. The author permitted
  distribution under the MIT License on 12 October 2026; see
  [`docs/permissions/MOSHIER_PERMISSION.md`](docs/permissions/MOSHIER_PERMISSION.md).
* **ELP 2000-82B.** The lunar series are from M. Chapront-Touzé and
  J. Chapront, CDS catalogue VI/79. The evaluator (`src/elp82b.c`) is JME's
  own, written from the published theory. The earlier third-party ELP
  implementation by Serhii Tsyba has been removed.
* **VSOP87.** The series are from P. Bretagnon and G. Francou, official IMCCE
  VSOP87A files. The evaluator (`src/vsop87.c`) is JME's own. The earlier
  generated code by Greg A. Miller (VSOP87-Multilang) has been removed.
* **ΔT.**
  * Stephenson, Morrison & Hohenkerk 2016 and the 2021 addendum (Table S15
    splines).
  * Morrison & Stephenson 2004 (Table 1).
  * Espenak & Meeus (NASA polynomials).
  * IERS finals2000A observed and predicted UT1−UTC, and IERS Bulletin C
    leap seconds.
  * Lunar tidal acceleration values from Chapront et al. 2002, Williams et
    al. 2008 and Folkner et al. 2014.
* **ERFA** (BSD 3-Clause, NumFOCUS Foundation): vendored subset.
* **CALCEPH** (CeCILL-B): optional, linked externally. CI builds CALCEPH
  5.0.1; 4.0.5 is also supported (see `THIRD_PARTY_NOTICES.md`). JPL DE
  kernels are distributed unmodified, outside this repository.
