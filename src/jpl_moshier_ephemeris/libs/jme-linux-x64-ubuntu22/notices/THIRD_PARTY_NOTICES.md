# Third-Party Notices

This file lists third-party science, data, and code used by **JPL Moshier Ephemeris (JME)**, the C library in this repository. The MIT License in [`LICENSE`](LICENSE) covers the original JME code written by Jayesh Mepani (Jayesh Patel). Unless stated otherwise below (the Moshier material is MIT by permission of its author), the components below are not relicensed by that MIT License; each keeps its own terms.

This file is informational and is not legal advice.

## Summary

| Component | Terms | Where it is used |
|---|---|---|
| CALCEPH 4.0.5 and 5.0.1 | CeCILL-B (CALCEPH is offered under CeCILL-C, CeCILL-B, or CeCILL v2.1; JME uses it under CeCILL-B) | Optional external library for the JPL engine; linked, not vendored in this repository |
| JPL DE440 / DE440s / DE441 kernels | NAIF rules: redistribution permitted if unmodified | Kernel files published unmodified in the [`jpl-kernels` release](https://github.com/jayeshmepani/jpl-ephemeris/releases/tag/jpl-kernels); not in this repository |
| Moshier planetary and lunar theories | Copyright Stephen L. Moshier; MIT License by permission of the author (12 October 2026, [record](docs/permissions/MOSHIER_PERMISSION.md)) | Moshier engine (`src/moshier_full.c`, `src/moshier_moon.c`, `src/moshier/`) |
| ELP 2000-82B lunar theory | Theory and series data: Chapront-Touzé & Chapront, CDS catalogue VI/79 (CDS data, attribution). Evaluator written for JME (MIT) from the published theory | Moon in the VSOP87 + ELP2000 + Meeus engine (`src/elp82b.c`, generated `src/elp82b_data.inc`, generator `tools/gen_elp82b.py`) |
| VSOP87A series data | Bretagnon & Francou 1988 (Bureau des Longitudes / IMCCE); official files from ftp.imcce.fr and CDS VI/81 (scientific data, attribution). Evaluator written for JME (MIT) | Planets in the VSOP87 + ELP2000 + Meeus engine (`src/vsop87.c`, generated `src/vsop87a_data.inc`, generator `tools/gen_vsop87a.py`, unmodified source files in `tools/data/vsop87/`) |
| ERFA 2.0.x (vendored subset, renamed `jme_era*`) | BSD 3-Clause, Copyright (C) 2013-2023 NumFOCUS Foundation | Precession, nutation, frame bias, sidereal time, polar motion (`pom00`, `sp00`), light deflection, aberration, star space motion, FK5->ICRS, TT/TDB/TCB/TCG and calendar conversions (`src/erfa/`, `src/erfa/vendor/`) |
| Meeus, *Astronomical Algorithms* | Formulas cited; no text or programs copied | Low-precision Sun/Moon arguments and mean elements (`src/meeus.c`) |
| Espenak & Meeus ΔT polynomials | NASA publication | ΔT model `ESPENAK_MEEUS_2006` (`src/time.c`) |
| Stephenson, Morrison & Hohenkerk 2016 ΔT splines (Table S15, 2016) | Published data (Proc. R. Soc. A, open access, CC BY 4.0); official supplementary ASCII table | ΔT model `STEPHENSON_ETC_2016` (`src/deltat_data.inc`, `tools/data/Table-S15.2016.txt`) |
| Morrison, Stephenson, Hohenkerk & Zawilski 2021 ΔT splines (Table S15, 2020 revision) | Published data (Proc. R. Soc. A, open access, CC BY 4.0); transcribed via Skyfield (MIT) | ΔT models `STEPHENSON_ETC_2021` and `AUTOMATIC` (`src/deltat_data.inc`, `tools/data/Table-S15.2020.csv`) |
| Morrison & Stephenson 2004 ΔT Table 1 | Published values (J. Hist. Astron. 35, 327), transcribed from the ADS scan and checked row by row | ΔT model `MS2004_TABLE1_LINEAR` (`src/deltat_ms2004_data.inc`, `tools/data/MS2004_Table1.txt`) |
| IERS Earth orientation data (finals2000A) | Public IERS data | Observed/predicted ΔT for `AUTOMATIC` (`src/deltat_data.inc`, `tools/data/finals2000A.all`); polar motion when loaded by the caller (`src/eop.c`) |
| NASA Five Millennium Catalog of Lunar Eclipses (Espenak & Meeus 2009) | NASA publication | Test reference only (`tools/data/NASA_LEcat5_2001-2100.txt`, `tests/test_lunar_eclipse_canon.c`) |
| Yale Bright Star Catalogue, 5th Rev. Ed. | NSSDC/ADC catalogue (CDS V/50) | Fixed-star names, catalogue and radial velocities (`src/fixstar_catalog.inc`) |
| Hipparcos, the New Reduction (van Leeuwen 2007) and Hipparcos 1997 HD index | ESA / CDS catalogues I/311 and I/239 (attribution) | Fixed-star astrometry overlay (`src/fixstar_hipparcos.inc`, generator `tools/gen_fixstar_hipparcos.py`, input `tools/data/bsc5_hipparcos2007.csv`) |
| IAU 2009 System of Astronomical Constants | Published constants (Luzum et al. 2011) | Planetary mass ratios for the analytical solar-system barycentre (`src/calc.c`) |
| IERS Bulletin C (leap seconds) | Public IERS data | Embedded TAI-UTC table (`src/time.c`) |
| Ayanamsa reference definitions | Published values (cited in `docs/AYANAMSA_MODELS.md`) | Sidereal zodiac models (`src/sidereal.c`) |

## CALCEPH

CALCEPH is not vendored in this repository. When JME is built with CALCEPH support it links to an external CALCEPH installation.

- Software: CALCEPH. JME's CI builds against CALCEPH 5.0.1, the current stable release. The Android/iOS libraries of the Dart package build against CALCEPH 4.0.5; the desktop prebuilt runtimes shipped with the binding packages (built through vcpkg) bundle CALCEPH 5.0.1.
- CALCEPH 4.0.5: Copyright 2008-2025 CNRS, Observatoire de Paris, Observatoire de la Côte d'Azur. Contributed by M. Gastineau, J. Laskar, H. Manche (ASD/IMCCE, Observatoire de Paris) and A. Fienga (Observatoire de la Côte d'Azur).
- CALCEPH 5.0.1: Copyright 2008-2026 CNRS. Main authors M. Gastineau, H. Manche, A. Fienga and J. Laskar (LTE, Observatoire de Paris, CNRS, PSL Research University, Sorbonne Université).
- Licence: CALCEPH is triple-licensed (CeCILL-C, CeCILL-B, or CeCILL v2.1). The JME ecosystem uses and redistributes it under the **CeCILL-B** Free Software License Agreement, version 1.0.
- Licence text: https://cecill.info/licences/Licence_CeCILL-B_V1-en.html (the binding packages that bundle CALCEPH also include the full text as `LICENSES/CeCILL-B.txt`).
- Source code: https://calceph.imcce.fr/ ; CALCEPH 4.0.5 source archive: https://www.imcce.fr/content/medias/recherche/equipes/asd/calceph/calceph-4.0.5.tar.gz ; CALCEPH 5.0.1 source archive: https://calceph.imcce.fr/releases/calceph-5.0.1.tar.gz (SHA-256 `923d5db2fca10636b64e5529552edf1de8bd3da1da3cc7ac963ae6c3895a31ae`)
- Project page and documentation: https://calceph.imcce.fr/

**No warranty (CeCILL-B Articles 8 and 9).** CALCEPH is provided by its licensors with only the limited warranty and limited liability described in Articles 8 and 9 of the CeCILL-B agreement. As stated in the CALCEPH copying conditions: "users are provided only with a limited warranty and the software's author, the holder of the economic rights, and the successive licensors have only limited liability." JME and its packages do not add any warranty on behalf of the CALCEPH authors.

JME and its bindings call CALCEPH through its public API as a separate library. The CALCEPH copyright notices inside the binaries are kept unchanged.

## JPL DE440 / DE440s / DE441 ephemerides

Planetary and lunar ephemerides DE440 and DE441: R. S. Park, W. M. Folkner, J. G. Williams, D. H. Boggs, "The JPL Planetary and Lunar Ephemerides DE440 and DE441", *The Astronomical Journal* 161, 105 (2021). Produced by NASA/JPL.

The kernel files are downloaded from JPL and republished unmodified (DE441 is split into parts only to fit GitHub's asset size limit; joining the parts in order restores the original file; the release includes SHA-256 checksums). The NAIF rules (https://naif.jpl.nasa.gov/naif/rules.html) state: "Redistribution of SPICE kernels distributed by NAIF is permitted as long as they have not been modified." Acknowledgement of JPL/NAIF is encouraged by those rules.

## Moshier planetary and lunar theories

The Moshier engine uses Stephen L. Moshier's analytical planetary theories ("plan404") and lunar theory from his Astronomical Almanac (AA) version 5.6, which are fits to the JPL DE404 ephemeris, together with code adapted from his `gplan.c` evaluation routines.

- Author: Stephen L. Moshier (http://www.moshier.net/).
- The original plan404 and AA 5.6 files carry no explicit license of their own. On **12 October 2026** Stephen L. Moshier gave permission to distribute "the material posted to the net" under an MIT license. That covers the plan404 tables and GPLAN.C, and the AA 5.6 / cmoon lunar tables and routines used here. The request and the verbatim reply are recorded in [`docs/permissions/MOSHIER_PERMISSION.md`](docs/permissions/MOSHIER_PERMISSION.md).
- This material is therefore distributed in JME under the MIT License (`LICENSE`), with the credit: *"Portions derived from the work of Stephen L. Moshier, incorporated herein by permission of the author."*
- The underlying method (periodic series fitted to a numerical JPL integration) is credited to Moshier.

## ELP 2000-82B lunar theory

- Theory and data: M. Chapront-Touzé and J. Chapront, "The lunar ephemeris ELP 2000", *Astronomy & Astrophysics* 124, 50 (1983), and "ELP 2000-85: a semi-analytical lunar ephemeris adequate for historical times", *A&A* 190, 342 (1988). Series data: CDS catalogue VI/79 (https://cdsarc.cds.unistra.fr/viz-bin/cat/VI/79), files ELP1 to ELP36.
- `src/elp82b_data.inc` is generated from the unmodified CDS files by `tools/gen_elp82b.py`, which verifies each file's SHA-256 digest before conversion. All terms of all 36 series are kept (no truncation).
- `src/elp82b.c` is an evaluator written for JME from the published theory and the documented reference evaluation procedure distributed with VI/79; it was checked against the official reference program's output. It is JME code under the MIT License.
- The earlier third-party ELP2000 C implementation (`src/elp2000/`, by Serhii Tsyba, no license file) has been **removed** from the repository.

## VSOP87

- Theory and data: P. Bretagnon and G. Francou, "Planetary theories in rectangular and spherical variables: VSOP87 solutions", *Astronomy & Astrophysics* 202, 309 (1988); Bureau des Longitudes. Series data: CDS catalogue VI/81 (https://cdsarc.cds.unistra.fr/viz-bin/cat/VI/81).
- Data: the unmodified official IMCCE files VSOP87A.mer … VSOP87A.nep, VSOP87A.emb, VSOP87A.ear and the reference check file vsop87.chk (https://ftp.imcce.fr/pub/ephem/planets/vsop87/, also CDS VI/81), stored in `tools/data/vsop87/` and pinned by SHA-256 in the generators.
- `src/vsop87a_data.inc` is generated by `tools/gen_vsop87a.py`. It keeps all 42,520 terms (no truncation) with coefficients copied as decimal text. `tests/fixtures/vsop87a_check.h` is generated from vsop87.chk by `tools/gen_vsop87_check.py`.
- `src/vsop87.c` (series evaluation with compensated summation and analytic time derivatives) is JME code under the MIT License.
- The earlier generated C code from VSOP87-Multilang (Greg A. Miller, public domain; `src/vsop87a_full.c`, `src/vsop87d_full.c`) has been **removed** from the repository.

## Meeus formulas

Some low-precision formulas (Sun and Moon fundamental arguments, mean orbital elements) follow Jean Meeus, *Astronomical Algorithms* (2nd ed., Willmann-Bell, 1998), which is cited as the source. No text, tables, or programs from the book are reproduced.

## Delta T (ΔT)

ΔT polynomials: F. Espenak and J. Meeus, *Five Millennium Canon of Solar Eclipses: -1999 to +3000*, NASA Technical Publication TP-2006-214141; polynomial expressions published by NASA GSFC at https://eclipse.gsfc.nasa.gov/SEhelp/deltatpoly2004.html.

## ΔT data

- Espenak & Meeus: see above.
- F. R. Stephenson, L. V. Morrison and C. Y. Hohenkerk 2016 (cited below): their official supplementary Table S15 (2016 edition, ASCII, from the Europe PMC supplementary archive of the article) is kept unmodified in `tools/data/Table-S15.2016.txt` (SHA-256 checked by `tools/gen_deltat.py`).
- L. V. Morrison and F. R. Stephenson, "Historical values of the Earth's clock error ΔT and the calculation of eclipses", *J. Hist. Astron.* 35, 327 (2004), Table 1 (p. 332), used with the authors' stated rule "intermediate figures for ΔT can be found with adequate precision by simple interpolation" (p. 331) and their parabola −20 + 32t² outside the table.
- Lunar tidal acceleration values for the ΔT correction: Chapront, Chapront-Touzé & Francou 2002 (*A&A* 387, 700, Table 7); Williams, Boggs & Folkner 2008 (JPL IOM 335-JW,DB,WF-20080314-001); Folkner et al. 2014 (IPN Progress Report 42-196).
- F. R. Stephenson, L. V. Morrison and C. Y. Hohenkerk, "Measurement of the Earth's rotation: 720 BC to AD 2015", *Proc. R. Soc. A* 472: 20160404 (2016), and L. V. Morrison, F. R. Stephenson, C. Y. Hohenkerk and M. Zawilski, "Addendum 2020 to 'Measurement of the Earth's rotation: 720 BC to AD 2015'", *Proc. R. Soc. A* 477: 20200776 (2021). The cubic-spline coefficients of their Table S15 (2020 revision, published by HM Nautical Almanac Office at https://astro.ukho.gov.uk/nao/lvm/) are kept unmodified in `tools/data/Table-S15.2020.csv`; they were transcribed from the copy bundled with Skyfield 1.55 (Brandon Rhodes, MIT License; file `skyfield/data/delta_t.npz`, SHA-256 recorded in the CSV header) because the HMNAO server was unreachable when the data were added.
- IERS Rapid Service/Prediction Centre (USNO) and IERS Earth Orientation Centre: `finals2000A.all` (Bulletin A and Bulletin B UT1-UTC), from https://datacenter.iers.org/data/9/finals2000A.all, kept unmodified in `tools/data/finals2000A.all` (SHA-256 checked by `tools/gen_deltat.py`).

## Yale Bright Star Catalogue

Fixed-star names, identifiers, magnitudes and radial velocities are taken from the Bright Star Catalogue, 5th Revised Edition, D. Hoffleit and W. H. Warren Jr., NASA NSSDC/ADC (1991), CDS catalogue V/50 (https://cdsarc.cds.unistra.fr/viz-bin/cat/V/50).

## Hipparcos astrometry

For bright stars with a Hipparcos counterpart, positions (ICRS, epoch J1991.25), proper motions and parallaxes are taken from *Hipparcos, the New Reduction of the Raw Data*, F. van Leeuwen, A&A 474, 653 (2007), CDS catalogue I/311, cross-identified through the HD numbers of *The Hipparcos and Tycho Catalogues*, ESA SP-1200 (1997), CDS catalogue I/239. The join was produced with the CDS VizieR TAP service (https://tapvizier.cds.unistra.fr/); the query is recorded in `tools/gen_fixstar_hipparcos.py`. This research has made use of the VizieR catalogue access tool, CDS, Strasbourg, France. Spot checks used the SIMBAD database, operated at CDS, Strasbourg, France.

## IAU 2009 constants, IERS data and ayanamsa definitions

- Sun/planet mass ratios: B. Luzum et al., "The IAU 2009 system of astronomical constants: the report of the IAU working group on numerical standards for Fundamental Astronomy", *Celestial Mechanics and Dynamical Astronomy* 110, 293 (2011).
- Leap seconds (TAI-UTC): IERS Bulletin C (https://hpiers.obspm.fr/iers/bul/bulc/), latest used: Bulletin C 72 (no leap second at the end of December 2026).
- Galactic-centre anchor: M. J. Reid and A. Brunthaler, "The Proper Motion of Sagittarius A*", *ApJ* 616, 872 (2004).
- Lahiri / ICRC definition and the Indian Astronomical Ephemeris values used for verification: Positional Astronomy Centre, India Meteorological Department, *Indian Astronomical Ephemeris* (published values only). Other ayanamsa definitions and their sources are listed in `docs/AYANAMSA_MODELS.md`; only published defining constants are used.

## ERFA (Essential Routines for Fundamental Astronomy)

JME vendors an unmodified-in-substance subset of ERFA (https://github.com/liberfa/erfa), which is derived from the IAU SOFA library. The files are in `src/erfa/` and `src/erfa/vendor/`; public symbols were renamed from `era*` to `jme_era*` to avoid link clashes, and the ERFA licence is kept in `src/erfa/vendor/LICENSE.ERFA`. The vendored routines cover frame bias, precession (IAU 1976, IAU 2006, Vondrák et al. 2011 long-term), nutation (IAU 1980, 2000A, 2000B, 2006A), obliquity, sidereal time and equation of the equinoxes, Earth rotation angle, polar-motion matrix and TIO locator (`pom00`, `sp00`), light deflection, aberration, star space motion, FK5 to Hipparcos (ICRS) catalogue transformation (`fk52h`, `fk5hip`), Earth position/velocity (`epv00`, used for checks only), TT/TDB/TCB/TCG conversions and calendar conversions. ERFA's terms require the following notice to be kept with source and binary redistributions:

```text
Copyright (C) 2013-2023, NumFOCUS Foundation.
All rights reserved.

This library is derived, with permission, from the International
Astronomical Union's "Standards of Fundamental Astronomy" library,
available from http://www.iausofa.org.

The ERFA version is intended to retain identical functionality to
the SOFA library, but made distinct through different function and
file names, as set out in the SOFA license conditions.  The SOFA
original has a role as a reference standard for the IAU and IERS,
and consequently redistribution is permitted only in its unaltered
state.  The ERFA version is not subject to this restriction and
therefore can be included in distributions which do not support the
concept of "read only" software.

Although the intent is to replicate the SOFA API (other than
replacement of prefix names) and results (with the exception of
bugs;  any that are discovered will be fixed), SOFA is not
responsible for any errors found in this version of the library.

If you wish to acknowledge the SOFA heritage, please acknowledge
that you are using a library derived from SOFA, rather than SOFA
itself.


TERMS AND CONDITIONS

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1 Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

2 Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the
  distribution.

3 Neither the name of the Standards Of Fundamental Astronomy Board,
  the International Astronomical Union nor the names of its
  contributors may be used to endorse or promote products derived
  from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```

## Contact

Questions or corrections about these notices: open an issue at https://github.com/jayeshmepani/jpl-ephemeris/issues.

## Test-fixture generators (not shipped in the library)

The scripts in `tools/gen_*_fixtures.py` compute independent reference values for the CTest certification tests. They use:

* Skyfield (Brandon Rhodes, MIT License);
* pyerfa / ERFA (BSD-3-Clause);
* astropy (BSD-3-Clause);
* SciPy (BSD-3-Clause);
* NumPy (BSD-3-Clause);
* the JPL DE440s ephemeris (NASA/JPL, public).

Only the numbers they produce are committed, as `tests/fixtures/*.h`, together with each generator's version line. No code from these packages is compiled into the engine.

The following publications were consulted for definitions and are cited in the documentation:

* J. Laskar, "Secular terms of classical planetary theories using the results of general theory", *A&A* 157, 59 (1986), Tables 5 and 8, and its erratum *A&A* 164, 437 (1986) (see `docs/ACCURACY.md` §2.1);
* M. J. Reid and A. Brunthaler, *ApJ* 616, 872 (2004) (Sgr A* position for `GALCENT_0SAG`);
* R. Holden, *The Elements of House Division* (1977) (Meridian, Morinus and Horizontal house definitions);
