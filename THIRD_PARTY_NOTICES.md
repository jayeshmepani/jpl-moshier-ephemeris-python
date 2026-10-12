# Third-Party Notices

This package is a binding for **JPL Moshier Ephemeris (JME)**, the C library at https://github.com/jayeshmepani/jpl-ephemeris. It ships prebuilt JME runtime libraries and prebuilt **CALCEPH 4.0.5** runtime libraries. The MIT License in [`LICENSE`](LICENSE) covers the original code written by Jayesh Mepani (Jayesh Patel). Unless stated otherwise below (the Moshier material is MIT by permission of its author), the components below are not relicensed by that MIT License; each keeps its own terms.

**Package license (as distributed): `MIT AND CeCILL-B`.** Project-authored code is MIT; the bundled CALCEPH 4.0.5 binaries are CeCILL-B; the Moshier material compiled into the JME runtime is MIT by permission of its author (12 October 2026); the ELP2000-82B implementation in the current runtime is permission-pending and is replaced in the upcoming JME release (see below).

This file is informational and is not legal advice.

## Summary

| Component | Terms | Where it is used |
|---|---|---|
| CALCEPH 4.0.5 | CeCILL-B (CALCEPH is offered under CeCILL-C, CeCILL-B, or CeCILL v2.1; JME uses it under CeCILL-B) | Bundled prebuilt runtime libraries (`libcalceph` / `calceph.dll` / `Calceph.xcframework`), unmodified |
| JPL DE440 / DE440s / DE441 kernels | NAIF rules: redistribution permitted if unmodified | Kernel files published unmodified in the [`jpl-kernels` release](https://github.com/jayeshmepani/jpl-ephemeris/releases/tag/jpl-kernels); not bundled in this package |
| Moshier planetary and lunar theories | Copyright Stephen L. Moshier; MIT License by permission of the author (12 October 2026, [record](https://github.com/jayeshmepani/jpl-ephemeris/blob/main/docs/permissions/MOSHIER_PERMISSION.md)) | Moshier engine (compiled into the JME runtime) |
| ELP2000-82B implementation | Code by Serhii Tsyba; no license file; permission pending (replaced in upcoming JME release by JME's own CDS-based evaluator). Theory/data: Chapront-Touzé & Chapront, CDS VI/79 | Moon in the VSOP87 + ELP2000 + Meeus engine (compiled into the JME runtime) |
| VSOP87 code (VSOP87-Multilang) | Greg A. Miller: public domain dedication. Theory/data: Bretagnon & Francou 1988, CDS VI/81 | Planets in the VSOP87 + ELP2000 + Meeus engine (compiled into the JME runtime) |
| ERFA (IAU 2000B nutation) | BSD 3-Clause, Copyright (C) 2013-2023 NumFOCUS Foundation | Nutation (compiled into the JME runtime) |
| Meeus, *Astronomical Algorithms* | Formulas cited; no text or programs copied | Low-precision Sun/Moon arguments and mean elements |
| Espenak & Meeus ΔT polynomials | NASA publication | ΔT model |
| Yale Bright Star Catalogue, 5th Rev. Ed. | NSSDC/ADC catalogue (CDS V/50) | Fixed stars |

## CALCEPH

**Bundled binary notice.** This package redistributes unmodified prebuilt runtime libraries of CALCEPH 4.0.5 so that the JPL engine works without a separate install.

- Software: CALCEPH 4.0.5
- Copyright 2008-2025 CNRS, Observatoire de Paris, Observatoire de la Côte d'Azur. Contributed by M. Gastineau, J. Laskar, H. Manche (ASD/IMCCE, Observatoire de Paris) and A. Fienga (Observatoire de la Côte d'Azur).
- Licence: CALCEPH is triple-licensed (CeCILL-C, CeCILL-B, or CeCILL v2.1). The JME ecosystem uses and redistributes it under the **CeCILL-B** Free Software License Agreement, version 1.0.
- Licence text: included in this repository as [`LICENSES/CeCILL-B.txt`](LICENSES/CeCILL-B.txt) (copied from `COPYING_CECILL_B.LIB` in the official CALCEPH 4.0.5 source distribution, converted to UTF-8). Official page: https://cecill.info/licences/Licence_CeCILL-B_V1-en.html
- Source code: https://calceph.imcce.fr/ ; CALCEPH 4.0.5 source archive: https://www.imcce.fr/content/medias/recherche/equipes/asd/calceph/calceph-4.0.5.tar.gz
- Project page and documentation: https://calceph.imcce.fr/

**No warranty (CeCILL-B Articles 8 and 9).** CALCEPH is provided by its licensors with only the limited warranty and limited liability described in Articles 8 and 9 of the CeCILL-B agreement. As stated in the CALCEPH copying conditions: "users are provided only with a limited warranty and the software's author, the holder of the economic rights, and the successive licensors have only limited liability." JME and its packages do not add any warranty on behalf of the CALCEPH authors.

JME and its bindings call CALCEPH through its public API as a separate library. The CALCEPH copyright notices inside the binaries are kept unchanged.

## JPL DE440 / DE440s / DE441 ephemerides

Planetary and lunar ephemerides DE440 and DE441: R. S. Park, W. M. Folkner, J. G. Williams, D. H. Boggs, "The JPL Planetary and Lunar Ephemerides DE440 and DE441", *The Astronomical Journal* 161, 105 (2021). Produced by NASA/JPL.

The kernel files are downloaded from JPL and republished unmodified (DE441 is split into parts only to fit GitHub's asset size limit; joining the parts in order restores the original file; the release includes SHA-256 checksums). The NAIF rules (https://naif.jpl.nasa.gov/naif/rules.html) state: "Redistribution of SPICE kernels distributed by NAIF is permitted as long as they have not been modified." Acknowledgement of JPL/NAIF is encouraged by those rules.

## Moshier planetary and lunar theories

The Moshier engine uses Stephen L. Moshier's analytical planetary theories ("plan404") and lunar theory from his Astronomical Almanac (AA) version 5.6, which are fits to the JPL DE404 ephemeris, together with code adapted from his `gplan.c` evaluation routines.

- Author: Stephen L. Moshier (http://www.moshier.net/).
- The original plan404 and AA 5.6 files carry no explicit license of their own. On **12 October 2026** Stephen L. Moshier gave permission to distribute "the material posted to the net" under an MIT license. That covers the plan404 tables and GPLAN.C, and the AA 5.6 / cmoon lunar tables and routines used in JME. The request and the verbatim reply are recorded in the C repository: https://github.com/jayeshmepani/jpl-ephemeris/blob/main/docs/permissions/MOSHIER_PERMISSION.md
- This material is therefore distributed under the MIT License, with the credit: *"Portions derived from the work of Stephen L. Moshier, incorporated herein by permission of the author."*
- The underlying method (periodic series fitted to a numerical JPL integration) is credited to Moshier.

## ELP2000-82B lunar theory and implementation

- Theory and data: M. Chapront-Touzé and J. Chapront, "The lunar ephemeris ELP 2000", *Astronomy & Astrophysics* 124, 50 (1983), and "ELP 2000-85: a semi-analytical lunar ephemeris adequate for historical times", *A&A* 190, 342 (1988). Series data: CDS catalogue VI/79 (https://cdsarc.cds.unistra.fr/viz-bin/cat/VI/79).
- C implementation: the files in the JME `src/elp2000/` directory come from Serhii Tsyba's `elp2000-82b` project (https://github.com/variar/elp2000-82b), "Created by Serhii Tsyba". That project has **no license file**, so this code is **not** covered by JME's MIT License.
- Status: permission to redistribute this code with attribution is **pending**. This notice does not claim that permission has been granted. The code is replaced in the upcoming JME release by JME's own ELP 2000-82B evaluator, generated from the unmodified CDS VI/79 series ([jpl-ephemeris PR #3](https://github.com/jayeshmepani/jpl-ephemeris/pull/3)); the prebuilt runtimes here will be rebuilt from it.

## VSOP87

- Theory and data: P. Bretagnon and G. Francou, "Planetary theories in rectangular and spherical variables: VSOP87 solutions", *Astronomy & Astrophysics* 202, 309 (1988); Bureau des Longitudes. Series data: CDS catalogue VI/81 (https://cdsarc.cds.unistra.fr/viz-bin/cat/VI/81).
- C code: generated by VSOP87-Multilang by Greg A. Miller (https://github.com/gmiller123456/vsop87-multilang). Its LICENSE states: "I release all of my work in this project to the public domain. Note, though, not everything here can be considered my work. The VSOP87 theory is the work of Bureau des Longitudes." The file headers ("Released as Public Domain") are kept.

## Meeus formulas

Some low-precision formulas (Sun and Moon fundamental arguments, mean orbital elements) follow Jean Meeus, *Astronomical Algorithms* (2nd ed., Willmann-Bell, 1998), which is cited as the source. No text, tables, or programs from the book are reproduced.

## Delta T (ΔT)

ΔT polynomials: F. Espenak and J. Meeus, *Five Millennium Canon of Solar Eclipses: -1999 to +3000*, NASA Technical Publication TP-2006-214141; polynomial expressions published by NASA GSFC at https://eclipse.gsfc.nasa.gov/SEhelp/deltatpoly2004.html.

## Yale Bright Star Catalogue

Fixed-star data are taken from the Bright Star Catalogue, 5th Revised Edition, D. Hoffleit and W. H. Warren Jr., NASA NSSDC/ADC (1991), CDS catalogue V/50 (https://cdsarc.cds.unistra.fr/viz-bin/cat/V/50).

## ERFA (Essential Routines for Fundamental Astronomy)

JME's IAU 2000B nutation routine is ported from ERFA's `nut00b.c` (https://github.com/liberfa/erfa), which is derived from the IAU SOFA library. ERFA's terms require the following notice to be kept with source and binary redistributions:

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

## Native engine notices

The bundled native runtimes are built from jpl-ephemeris commit c15031e. Their attribution is in [`NOTICE.md`](NOTICE.md). The vendored ERFA licence (BSD-3-Clause) is in [`LICENSES/LICENSE.ERFA`](LICENSES/LICENSE.ERFA). Each runtime folder carries its own `notices/` copy, including `JME_NATIVE_COMMIT.txt`.
